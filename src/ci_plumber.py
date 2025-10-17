#!/usr/bin/env python3

from github import Github
from .config_loader import ConfigLoader
from .logger_setup import setup_logging
from .github_handler import GitHubHandler
from .linter_fixer import LinterFixer
from .chromatic_handler import ChromaticHandler


class CIPlumber:
    def __init__(self, config_path="cfg/config.yaml"):
        self.config = ConfigLoader.load(config_path)
        self._validate_config()
        self.logger = setup_logging(self.config)
        self.github = Github(self.config["github"]["token"])
        self.repo = self.github.get_repo(self.config["github"]["repo"])
        
        self.token_owner = self.github.get_user().login
        self.allowed_authors = self._build_allowed_authors()
        self.logger.info(f"🔑 Detected token owner: {self.token_owner}")
        self.logger.info(f"👥 Allowed PR authors: {', '.join(self.allowed_authors)}")
        
        self.github_handler = GitHubHandler(self.repo, self.config, self.logger)
        self.linter_fixer = LinterFixer(self.config, self.logger)
        self.chromatic_handler = ChromaticHandler(self.repo, self.logger)
    
    def _validate_config(self):
        if "authors" not in self.config:
            raise ValueError(
                "Missing 'authors' section in config.yaml. Please add:\n"
                "authors:\n"
                "  include_token_owner: true\n"
                "  allowed_users: []"
            )
    
    def _build_allowed_authors(self):
        authors_config = self.config["authors"]
        allowed = list(authors_config.get("allowed_users", []))
        
        if authors_config.get("include_token_owner", True):
            if self.token_owner not in allowed:
                allowed.insert(0, self.token_owner)
        
        return allowed
    
    def run(self):
        print("\033[0;36m\033[1m")
        print("╔════════════════════════════════════════════════════════════════════════════════╗")
        print("║                          🔧 CI Plumber Starting...                            ║")
        print("╚════════════════════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        self.logger.info("Starting CI Plumber run")
        
        try:
            all_prs = self.github_handler.find_target_prs()
            self.logger.info(f"🔍 Found {len(all_prs)} PRs with label '{self.config['labels']['trigger']}'")
            
            prs = self._filter_by_authors(all_prs)
            self.logger.info(f"👥 Processing {len(prs)} PRs from allowed authors")
            
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
    
    def _process_pr(self, pr):
        try:
            self.github_handler.ensure_required_labels(pr)
            
            self.github_handler.check_and_update_branch(pr)
            
            ci_status = self.github_handler.check_ci_status(pr)
            self.logger.info(f"🔍 PR #{pr.number} CI status: {ci_status}")
            
            if "linter_failed" in ci_status:
                self.logger.info(f"🔧 PR #{pr.number} has linter failures, attempting fix")
                self.linter_fixer.fix_linter_issues(pr)
            
            if "chromatic_failed" in ci_status:
                self.logger.info(f"🎨 PR #{pr.number} has chromatic failures, retrying workflow")
                self.chromatic_handler.retry_chromatic(pr)
            
            if self.github_handler.can_merge(pr):
                self.logger.info(f"✅ PR #{pr.number} is ready to merge")
                self.github_handler.merge_pr(pr)
            else:
                self.logger.warning(f"⏸️  PR #{pr.number} is not ready to merge yet - see reasons above")
                
        except Exception as e:
            self.logger.error(f"Error processing PR #{pr.number}: {e}", exc_info=True)
    
    def _filter_by_authors(self, prs):
        filtered = []
        for pr in prs:
            author = pr.user.login
            if author in self.allowed_authors:
                self.logger.info(f"✓ PR #{pr.number} by {author} - authorized")
                filtered.append(pr)
            else:
                self.logger.info(f"⏭ PR #{pr.number} by {author} - skipping (not in allowed authors)")
        return filtered

