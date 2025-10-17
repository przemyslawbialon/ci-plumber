#!/usr/bin/env python3

from github import GithubException


class ChromaticHandler:
    def __init__(self, repo, logger):
        self.repo = repo
        self.logger = logger
    
    def retry_chromatic(self, pr):
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

