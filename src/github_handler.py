#!/usr/bin/env python3

from github import GithubException


class GitHubHandler:
    def __init__(self, repo, config, logger):
        self.repo = repo
        self.config = config
        self.logger = logger

    def find_target_prs(self):
        trigger_label = self.config["labels"]["trigger"]
        prs = []

        for pr in self.repo.get_pulls(state="open"):
            labels = [label.name for label in pr.labels]
            if trigger_label in labels:
                prs.append(pr)

        return prs

    def ensure_required_labels(self, pr):
        current_labels = [label.name for label in pr.labels]

        auto_add_labels = self.config["labels"].get("auto_add", [])
        for label in auto_add_labels:
            if label not in current_labels:
                self.logger.info(f"🏷️  Adding missing label '{label}' to PR #{pr.number}")
                try:
                    pr.add_to_labels(label)
                except GithubException as e:
                    self.logger.warning(f"⚠️  Failed to add label '{label}': {e}")

        label_categories = self.config["labels"].get("categories", [])
        for category in label_categories:
            prefix = category.get("prefix")
            default_label = category.get("default")

            if not prefix or not default_label:
                continue

            has_category_label = any(label.startswith(prefix) for label in current_labels)

            if not has_category_label:
                self.logger.info(
                    f"🏷️  Adding default label '{default_label}' "
                    f"for category '{prefix}' to PR #{pr.number}"
                )
                try:
                    pr.add_to_labels(default_label)
                except GithubException as e:
                    self.logger.warning(f"⚠️  Failed to add label '{default_label}': {e}")
            else:
                existing_label = next(
                    (label for label in current_labels if label.startswith(prefix)), None
                )
                self.logger.info(
                    f"ℹ️  Skipping category '{prefix}' - "
                    f"PR #{pr.number} already has '{existing_label}'"
                )

    def check_and_update_branch(self, pr):
        try:
            comparison = self.repo.compare(pr.base.ref, pr.head.ref)
            commits_behind = comparison.behind_by

            self.logger.info(f"📊 PR #{pr.number} is {commits_behind} commits behind {pr.base.ref}")

            if commits_behind > self.config["repository"]["max_commits_behind"]:
                self.logger.info(f"🔄 PR #{pr.number} is too far behind, triggering branch update")
                self._update_branch(pr)

        except GithubException as e:
            self.logger.error(f"Failed to check branch distance for PR #{pr.number}: {e}")

    def _update_branch(self, pr):
        try:
            pr.update_branch()
            self.logger.info(f"✅ Successfully triggered branch update for PR #{pr.number}")
        except GithubException as e:
            self.logger.error(f"❌ Failed to update branch for PR #{pr.number}: {e}")

    def check_ci_status(self, pr):
        statuses = []

        try:
            commit = self.repo.get_commit(pr.head.sha)

            combined_status = commit.get_combined_status()
            for status in combined_status.statuses:
                if status.state == "failure":
                    context = status.context.lower()
                    if "lint" in context or "eslint" in context:
                        statuses.append("linter_failed")
                    elif "chromatic" in context:
                        statuses.append("chromatic_failed")

            check_runs = commit.get_check_runs()
            for check in check_runs:
                if check.conclusion == "failure":
                    name = check.name.lower()
                    if "lint" in name or "eslint" in name:
                        statuses.append("linter_failed")
                    elif "chromatic" in name:
                        statuses.append("chromatic_failed")

        except Exception as e:
            self.logger.error(f"Error checking CI status for PR #{pr.number}: {e}")

        return list(set(statuses))

    def can_merge(self, pr):
        try:
            if pr.merged:
                self.logger.info(f"✅ PR #{pr.number} is already merged")
                return False

            if not pr.mergeable:
                self.logger.warning(
                    f"❌ PR #{pr.number} is not mergeable (conflicts or other issues)"
                )
                return False

            commit = self.repo.get_commit(pr.head.sha)
            combined_status = commit.get_combined_status()

            if combined_status.state not in ["success"]:
                if combined_status.state == "failure":
                    self.logger.warning(
                        f"❌ PR #{pr.number} combined status is 'failure' - CI checks failed"
                    )
                elif combined_status.state == "pending":
                    self.logger.info(
                        f"⏳ PR #{pr.number} combined status is 'pending' - waiting for CI"
                    )
                else:
                    self.logger.info(
                        f"⏳ PR #{pr.number} combined status is '{combined_status.state}'"
                    )
                return False

            check_runs = commit.get_check_runs()
            for check in check_runs:
                if check.conclusion not in ["success", "skipped", "neutral", None]:
                    self.logger.warning(
                        f"❌ PR #{pr.number} has failing check: {check.name} ({check.conclusion})"
                    )
                    return False

            approval_check = self._check_approvals(pr)
            if not approval_check["approved"]:
                self._log_missing_approvals(pr, approval_check)
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking if PR #{pr.number} can merge: {e}")
            return False

    def _check_approvals(self, pr):
        reviews = pr.get_reviews()
        approved_users = set()
        has_changes_requested = False

        for review in reviews:
            if review.state == "APPROVED":
                approved_users.add(review.user.login)
            elif review.state == "CHANGES_REQUESTED":
                has_changes_requested = True

        if has_changes_requested:
            return {"approved": False, "reason": "changes_requested"}

        minimum_approvals = self.config.get("approvals", {}).get("minimum_count", 2)
        approval_count = len(approved_users)

        if approval_count < minimum_approvals:
            return {
                "approved": False,
                "reason": "insufficient_approvals",
                "count": approval_count,
                "required": minimum_approvals,
            }

        try:
            requested_reviewers = pr.get_review_requests()
            requested_users = [user.login for user in requested_reviewers[0]]
            requested_teams = [team.slug for team in requested_reviewers[1]]

            missing_users = [user for user in requested_users if user not in approved_users]
            missing_teams = []

            for team in requested_teams:
                try:
                    team_obj = self.repo.organization.get_team_by_slug(team)
                    team_members = [member.login for member in team_obj.get_members()]

                    team_approved = any(member in approved_users for member in team_members)
                    if not team_approved:
                        missing_teams.append(team)
                except Exception as e:
                    self.logger.warning(f"⚠️  Could not check team '{team}': {e}")
                    missing_teams.append(team)

            if missing_users or missing_teams:
                return {
                    "approved": False,
                    "reason": "missing_requested_reviews",
                    "count": approval_count,
                    "required": minimum_approvals,
                    "missing_users": missing_users,
                    "missing_teams": missing_teams,
                }
        except Exception as e:
            self.logger.warning(f"⚠️  Could not check requested reviewers: {e}")

        return {"approved": True, "count": approval_count}

    def _log_missing_approvals(self, pr, approval_check):
        reason = approval_check.get("reason")

        if reason == "changes_requested":
            self.logger.warning(f"🔄 PR #{pr.number} has requested changes")

        elif reason == "insufficient_approvals":
            count = approval_check.get("count", 0)
            required = approval_check.get("required", 2)
            needed = required - count
            self.logger.warning(
                f"❌ PR #{pr.number} needs {needed} more approval(s) (current: {count}/{required})"
            )

        elif reason == "missing_requested_reviews":
            count = approval_check.get("count", 0)
            required = approval_check.get("required", 2)
            self.logger.warning(
                f"⏳ PR #{pr.number} has {count}/{required} approvals but missing requested reviews:"
            )

            missing_users = approval_check.get("missing_users", [])
            missing_teams = approval_check.get("missing_teams", [])

            if missing_teams:
                teams_str = ", ".join([f"@{team}" for team in missing_teams])
                self.logger.warning(f"   🏢 Missing team approvals: {teams_str}")

            if missing_users:
                users_str = ", ".join([f"@{user}" for user in missing_users])
                self.logger.warning(f"   👤 Missing user approvals: {users_str}")

    def merge_pr(self, pr):
        try:
            self.logger.info(f"🚀 Attempting to merge PR #{pr.number}")
            pr.merge(merge_method="squash")
            self.logger.info(f"🎉 Successfully merged PR #{pr.number}")
        except GithubException as e:
            self.logger.error(f"❌ Failed to merge PR #{pr.number}: {e}")
