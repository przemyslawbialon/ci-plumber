#!/usr/bin/env python3

import sys
import yaml
from github import Github, GithubException


def test_config():
    print("Testing CI Plumber configuration...")
    print("=" * 60)
    
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        print("✓ config.yaml loaded successfully")
    except FileNotFoundError:
        print("✗ config.yaml not found!")
        return False
    except yaml.YAMLError as e:
        print(f"✗ config.yaml parsing error: {e}")
        return False
    
    token = config.get("github", {}).get("token")
    if not token or token == "PLACEHOLDER_TOKEN_HERE":
        print("✗ GitHub token not configured in config.yaml")
        return False
    print("✓ GitHub token found in config")
    
    try:
        g = Github(token)
        user = g.get_user()
        print(f"✓ Successfully authenticated as: {user.login}")
    except GithubException as e:
        print(f"✗ GitHub authentication failed: {e}")
        return False
    
    repo_name = config.get("github", {}).get("repo")
    if not repo_name:
        print("✗ Repository not configured in config.yaml")
        return False
    
    try:
        repo = g.get_repo(repo_name)
        print(f"✓ Successfully accessed repository: {repo.full_name}")
    except GithubException as e:
        print(f"✗ Cannot access repository {repo_name}: {e}")
        return False
    
    trigger_label = config.get("labels", {}).get("trigger")
    if trigger_label:
        print(f"✓ Trigger label configured: {trigger_label}")
    else:
        print("✗ Trigger label not configured")
        return False
    
    auto_labels = config.get("labels", {}).get("auto_add", [])
    if auto_labels:
        print(f"✓ Auto-add labels configured: {', '.join(auto_labels)}")
    else:
        print("⚠ No auto-add labels configured")
    
    linter_cmd = config.get("linter", {}).get("fix_command")
    if linter_cmd:
        print(f"✓ Linter fix command configured: {linter_cmd}")
    else:
        print("✗ Linter fix command not configured")
        return False
    
    print("=" * 60)
    print("✓ All configuration checks passed!")
    print("\nYou can now run: python3 ci_plumber.py")
    return True


if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)

