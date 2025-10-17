#!/usr/bin/env python3

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent))

import yaml
from github import Github, GithubException


class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    BOLD = "\033[1m"
    NC = "\033[0m"


def test_config():
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          Testing CI Plumber Configuration 🧪             ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.NC}")

    try:
        config_path = Path(__file__).parent / "cfg" / "config.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        print(f"{Colors.GREEN}✓ cfg/config.yaml loaded successfully{Colors.NC}")
    except FileNotFoundError:
        print(f"{Colors.RED}✗ cfg/config.yaml not found!{Colors.NC}")
        return False
    except yaml.YAMLError as e:
        print(f"{Colors.RED}✗ cfg/config.yaml parsing error: {e}{Colors.NC}")
        return False

    token = config.get("github", {}).get("token")
    if not token or token == "PLACEHOLDER_TOKEN_HERE":
        print(f"{Colors.RED}✗ GitHub token not configured in cfg/config.yaml{Colors.NC}")
        return False
    print(f"{Colors.GREEN}✓ GitHub token found in config{Colors.NC}")

    try:
        g = Github(token)
        user = g.get_user()
        print(
            f"{Colors.GREEN}✓ Successfully authenticated as: {Colors.BOLD}{user.login}{Colors.NC}"
        )
    except GithubException as e:
        print(f"{Colors.RED}✗ GitHub authentication failed: {e}{Colors.NC}")
        return False

    repo_name = config.get("github", {}).get("repo")
    if not repo_name:
        print(f"{Colors.RED}✗ Repository not configured in cfg/config.yaml{Colors.NC}")
        return False

    try:
        repo = g.get_repo(repo_name)
        print(
            f"{Colors.GREEN}✓ Successfully accessed repository: {Colors.BOLD}{repo.full_name}{Colors.NC}"
        )
    except GithubException as e:
        print(f"{Colors.RED}✗ Cannot access repository {repo_name}: {e}{Colors.NC}")
        return False

    trigger_label = config.get("labels", {}).get("trigger")
    if trigger_label:
        print(f"{Colors.GREEN}✓ Trigger label configured: {Colors.CYAN}{trigger_label}{Colors.NC}")
    else:
        print(f"{Colors.RED}✗ Trigger label not configured{Colors.NC}")
        return False

    auto_labels = config.get("labels", {}).get("auto_add", [])
    if auto_labels:
        print(
            f"{Colors.GREEN}✓ Auto-add labels configured: {Colors.CYAN}{', '.join(auto_labels)}{Colors.NC}"
        )
    else:
        print(f"{Colors.YELLOW}⚠ No auto-add labels configured{Colors.NC}")

    linter_cmd = config.get("linter", {}).get("fix_command")
    if linter_cmd:
        print(
            f"{Colors.GREEN}✓ Linter fix command configured: {Colors.CYAN}{linter_cmd}{Colors.NC}"
        )
    else:
        print(f"{Colors.RED}✗ Linter fix command not configured{Colors.NC}")
        return False

    authors_config = config.get("authors")
    if authors_config:
        include_owner = authors_config.get("include_token_owner", True)
        allowed = authors_config.get("allowed_users", [])

        include_status = "enabled" if include_owner else "disabled"
        print(f"{Colors.GREEN}✓ Authors filtering: include token owner {include_status}{Colors.NC}")

        allowed_display = ", ".join(allowed) if allowed else "none"
        print(
            f"{Colors.GREEN}✓ Allowed additional users: {Colors.CYAN}{allowed_display}{Colors.NC}"
        )
    else:
        print(f"{Colors.RED}✗ Authors section not configured (required){Colors.NC}")
        return False

    print(f"\n{Colors.GREEN}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        ✓ All configuration checks passed! 🎉             ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.NC}")
    print(f"{Colors.CYAN}You can now run: {Colors.BOLD}python ci_plumber.py{Colors.NC}\n")
    return True


if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)
