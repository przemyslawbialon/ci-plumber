#!/usr/bin/env python3

import os
import sys
import yaml
import logging
from datetime import datetime
from pathlib import Path
import subprocess
import shutil

from github import Github, GithubException
from git import Repo, GitCommandError


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[0;36m',
        'INFO': '\033[0;32m',
        'WARNING': '\033[1;33m',
        'ERROR': '\033[0;31m',
        'CRITICAL': '\033[1;31m',
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    EMOJI = {
        'DEBUG': '🔍',
        'INFO': '📝',
        'WARNING': '⚠️ ',
        'ERROR': '❌',
        'CRITICAL': '🔥',
    }
    
    def format(self, record):
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            levelname = record.levelname
            if levelname in self.COLORS:
                emoji = self.EMOJI.get(levelname, '')
                record.levelname = f"{self.COLORS[levelname]}{emoji} {levelname}{self.RESET}"
                record.msg = f"{self.COLORS[levelname]}{record.msg}{self.RESET}"
        return super().format(record)


class CIPlumber:
    def __init__(self, config_path="config.yaml"):
        self.config = self._load_config(config_path)
        self._setup_logging()
        self.github = Github(self.config["github"]["token"])
        self.repo = self.github.get_repo(self.config["github"]["repo"])
        self.local_repo_path = self.config["repository"]["local_path"]
        
    def _load_config(self, config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    
    def _setup_logging(self):
        log_dir = Path(self.config["logging"]["directory"])
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"ci-plumber-{datetime.now().strftime('%Y-%m-%d')}.log"
        
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_formatter = ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s")
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(file_formatter)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, self.config["logging"]["level"]))
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def run(self):
        print("\033[0;36m\033[1m")
        print("╔════════════════════════════════════════════════════════════════════════════════╗")
        print("║                          🔧 CI Plumber Starting...                            ║")
        print("╚════════════════════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        self.logger.info("Starting CI Plumber run")
        
        try:
            prs = self._find_target_prs()
            self.logger.info(f"🔍 Found {len(prs)} PRs with label '{self.config['labels']['trigger']}'")
            
            for pr in prs:
                print(f"\n\033[1;34m{'='*80}\033[0m")
                self.logger.info(f"🔄 Processing PR #{pr.number}: {pr.title}")
                print(f"\033[1;34m{'='*80}\033[0m")
                self._process_pr(pr)
                
        except Exception as e:
            self.logger.error(f"💥 Fatal error during run: {e}", exc_info=True)
        
        print("\n\033[0;32m\033[1m")
        print("╔════════════════════════════════════════════════════════════════════════════════╗")
        print("║                        ✅ CI Plumber Run Completed!                           ║")
        print("╚════════════════════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
    
    def _find_target_prs(self):
        trigger_label = self.config["labels"]["trigger"]
        prs = []
        
        for pr in self.repo.get_pulls(state="open"):
            labels = [label.name for label in pr.labels]
            if trigger_label in labels:
                prs.append(pr)
        
        return prs
    
    def _process_pr(self, pr):
        try:
            self._ensure_required_labels(pr)
            
            self._check_and_update_branch(pr)
            
            ci_status = self._check_ci_status(pr)
            self.logger.info(f"🔍 PR #{pr.number} CI status: {ci_status}")
            
            if "linter_failed" in ci_status:
                self.logger.info(f"🔧 PR #{pr.number} has linter failures, attempting fix")
                self._fix_linter_issues(pr)
            
            if "chromatic_failed" in ci_status:
                self.logger.info(f"🎨 PR #{pr.number} has chromatic failures, retrying workflow")
                self._retry_chromatic(pr)
            
            if self._can_merge(pr):
                self.logger.info(f"✅ PR #{pr.number} is ready to merge")
                self._merge_pr(pr)
            else:
                self.logger.info(f"⏳ PR #{pr.number} is not ready to merge yet")
                
        except Exception as e:
            self.logger.error(f"Error processing PR #{pr.number}: {e}", exc_info=True)
    
    def _ensure_required_labels(self, pr):
        current_labels = [label.name for label in pr.labels]
        required_labels = self.config["labels"]["auto_add"]
        
        for required_label in required_labels:
            if required_label not in current_labels:
                self.logger.info(f"🏷️  Adding missing label '{required_label}' to PR #{pr.number}")
                try:
                    pr.add_to_labels(required_label)
                except GithubException as e:
                    self.logger.warning(f"⚠️  Failed to add label '{required_label}': {e}")
    
    def _check_and_update_branch(self, pr):
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
    
    def _check_ci_status(self, pr):
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
    
    def _fix_linter_issues(self, pr):
        try:
            self._ensure_local_repo()
            
            local_repo = Repo(self.local_repo_path)
            
            self.logger.info(f"📥 Fetching latest changes for PR #{pr.number}")
            local_repo.remotes.origin.fetch()
            
            branch_name = pr.head.ref
            self.logger.info(f"🔄 Checking out branch {branch_name}")
            
            try:
                local_repo.git.checkout(branch_name)
            except GitCommandError:
                local_repo.git.checkout("-b", branch_name, f"origin/{branch_name}")
            
            local_repo.remotes.origin.pull(branch_name)
            
            self.logger.info(f"🔧 Running linter fix command: {self.config['linter']['fix_command']}")
            result = subprocess.run(
                self.config["linter"]["fix_command"],
                shell=True,
                cwd=self.local_repo_path,
                capture_output=True,
                text=True
            )
            
            self.logger.info(f"📄 Linter command output: {result.stdout}")
            if result.stderr:
                self.logger.warning(f"⚠️  Linter command stderr: {result.stderr}")
            
            if local_repo.is_dirty():
                self.logger.info("💾 Committing linter fixes")
                local_repo.git.add(A=True)
                local_repo.index.commit("Fix linter issues (automated by CI Plumber)")
                
                self.logger.info("📤 Pushing linter fixes to remote")
                local_repo.remotes.origin.push(branch_name)
                
                self.logger.info(f"✅ Successfully fixed and pushed linter issues for PR #{pr.number}")
            else:
                self.logger.info("ℹ️  No linter changes to commit")
                
        except Exception as e:
            self.logger.error(f"Failed to fix linter issues for PR #{pr.number}: {e}", exc_info=True)
    
    def _ensure_local_repo(self):
        if not os.path.exists(self.local_repo_path):
            self.logger.info(f"📦 Cloning repository to {self.local_repo_path}")
            repo_url = f"https://{self.config['github']['token']}@github.com/{self.config['github']['repo']}.git"
            Repo.clone_from(repo_url, self.local_repo_path)
            self.logger.info("✅ Repository cloned successfully")
        else:
            self.logger.info(f"📂 Using existing repository at {self.local_repo_path}")
    
    def _retry_chromatic(self, pr):
        try:
            commit = self.repo.get_commit(pr.head.sha)
            check_runs = commit.get_check_runs()
            
            for check in check_runs:
                if "chromatic" in check.name.lower() and check.conclusion == "failure":
                    self.logger.info(f"🔄 Retrying check run: {check.name}")
                    try:
                        self.repo.get_check_run(check.id).rerequest()
                        self.logger.info(f"✅ Successfully requested re-run of {check.name}")
                    except GithubException as e:
                        self.logger.warning(f"⚠️  Could not re-run check {check.name}: {e}")
            
            workflows = self.repo.get_workflows()
            for workflow in workflows:
                if "chromatic" in workflow.name.lower():
                    runs = workflow.get_runs(branch=pr.head.ref, event="pull_request")
                    for run in runs:
                        if run.head_sha == pr.head.sha and run.conclusion == "failure":
                            self.logger.info(f"🔄 Re-running workflow: {workflow.name}")
                            try:
                                run.rerun()
                                self.logger.info(f"✅ Successfully re-ran workflow {workflow.name}")
                            except GithubException as e:
                                self.logger.warning(f"⚠️  Could not re-run workflow {workflow.name}: {e}")
                            break
                            
        except Exception as e:
            self.logger.error(f"Failed to retry chromatic for PR #{pr.number}: {e}", exc_info=True)
    
    def _can_merge(self, pr):
        try:
            if pr.merged:
                self.logger.info(f"✅ PR #{pr.number} is already merged")
                return False
            
            if not pr.mergeable:
                self.logger.info(f"❌ PR #{pr.number} is not mergeable (conflicts or other issues)")
                return False
            
            commit = self.repo.get_commit(pr.head.sha)
            combined_status = commit.get_combined_status()
            
            if combined_status.state not in ["success"]:
                self.logger.info(f"⏳ PR #{pr.number} combined status is '{combined_status.state}', not ready")
                return False
            
            check_runs = commit.get_check_runs()
            for check in check_runs:
                if check.conclusion not in ["success", "skipped", "neutral", None]:
                    self.logger.info(f"❌ PR #{pr.number} has failing check: {check.name} ({check.conclusion})")
                    return False
            
            reviews = pr.get_reviews()
            approved = False
            for review in reviews:
                if review.state == "APPROVED":
                    approved = True
                elif review.state == "CHANGES_REQUESTED":
                    self.logger.info(f"🔄 PR #{pr.number} has requested changes")
                    return False
            
            if not approved:
                self.logger.info(f"⏳ PR #{pr.number} is not approved yet")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking if PR #{pr.number} can merge: {e}")
            return False
    
    def _merge_pr(self, pr):
        try:
            self.logger.info(f"🚀 Attempting to merge PR #{pr.number}")
            pr.merge(merge_method="squash")
            self.logger.info(f"🎉 Successfully merged PR #{pr.number}")
        except GithubException as e:
            self.logger.error(f"❌ Failed to merge PR #{pr.number}: {e}")


def main():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    plumber = CIPlumber(config_path)
    plumber.run()


if __name__ == "__main__":
    main()

