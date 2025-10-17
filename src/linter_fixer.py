#!/usr/bin/env python3

import os
import subprocess
from git import Repo, GitCommandError


class LinterFixer:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.local_repo_path = config["repository"]["local_path"]
    
    def fix_linter_issues(self, pr):
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

