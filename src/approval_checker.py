#!/usr/bin/env python3


class ApprovalChecker:
    def __init__(self, repo, config, logger):
        self.repo = repo
        self.config = config
        self.logger = logger

    def check_approvals(self, pr):
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
            missing_teams = self._check_team_approvals(requested_teams, approved_users)

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

    def _check_team_approvals(self, requested_teams, approved_users):
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

        return missing_teams

    def log_missing_approvals(self, pr, approval_check):
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
                f"⏳ PR #{pr.number} has {count}/{required} approvals "
                f"but missing requested reviews:"
            )

            missing_users = approval_check.get("missing_users", [])
            missing_teams = approval_check.get("missing_teams", [])

            if missing_teams:
                teams_str = ", ".join([f"@{team}" for team in missing_teams])
                self.logger.warning(f"   🏢 Missing team approvals: {teams_str}")

            if missing_users:
                users_str = ", ".join([f"@{user}" for user in missing_users])
                self.logger.warning(f"   👤 Missing user approvals: {users_str}")
