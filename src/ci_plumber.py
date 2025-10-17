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
        self.logger = setup_logging(self.config)
        self.github = Github(self.config["github"]["token"])
        self.repo = self.github.get_repo(self.config["github"]["repo"])
        
        self.github_handler = GitHubHandler(self.repo, self.config, self.logger)
        self.linter_fixer = LinterFixer(self.config, self.logger)
        self.chromatic_handler = ChromaticHandler(self.repo, self.logger)
    
    def run(self):
        print("\033[0;36m\033[1m")
        print("╔════════════════════════════════════════════════════════════════════════════════╗")
        print("║                          🔧 CI Plumber Starting...                            ║")
        print("╚════════════════════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        self.logger.info("Starting CI Plumber run")
        
        try:
            prs = self.github_handler.find_target_prs()
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

