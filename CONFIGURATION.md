# Configuration Guide

Detailed guide for configuring CI Plumber.

## Author Filtering

CI Plumber can be configured to only process PRs from specific authors (whitelist).

### Configuration

```yaml
authors:
  include_token_owner: true  # Auto-include GitHub token owner
  allowed_users:
    - "teammate1"
    - "teammate2"
```

### Behavior

**`include_token_owner: true`** (default)
- Automatically detects your GitHub username from the token
- Adds you to the allowed authors list
- Useful for personal automation

**`allowed_users`**
- Additional GitHub usernames to process
- Can be empty list if you only want your own PRs

### Examples

#### Only your PRs
```yaml
authors:
  include_token_owner: true
  allowed_users: []
```

#### Your PRs + teammates
```yaml
authors:
  include_token_owner: true
  allowed_users:
    - "john-doe"
    - "jane-smith"
```

#### Only specific users (not you)
```yaml
authors:
  include_token_owner: false
  allowed_users:
    - "team-lead"
```

**Note**: The `authors` section is **required**. CI Plumber will fail to start if it's missing.

## Label Management

CI Plumber supports two types of label management:

### 1. Simple Auto-Add Labels

Labels that are always added if missing:

```yaml
labels:
  auto_add:
    - "workdays: Mon-Fri"
    - "priority: medium"
```

These labels will be added to any PR that doesn't have them.

### 2. Category-Based Labels

Labels with prefix-based logic - only adds default if no label with that prefix exists:

```yaml
labels:
  categories:
    - prefix: "Monoreason:"
      default: "Monoreason: Large effort"
    - prefix: "Team:"
      default: "Team: General"
```

**How it works:**
- If PR has **no** label starting with `Monoreason:` → adds `Monoreason: Large effort`
- If PR already has `Monoreason: Small effort` → **skips**, leaves existing label
- If PR already has `Monoreason: Medium effort` → **skips**, leaves existing label

This allows developers to set their own Monoreason but ensures there's always one present.

## Complete Configuration Example

```yaml
github:
  token: "ghp_yourtoken..."
  repo: "Dapulse/dapulse"

authors:
  include_token_owner: true
  allowed_users:
    - "teammate1"
  
labels:
  trigger: "ci-plumber-to-merge"
  
  auto_add:
    - "workdays: Mon-Fri"
    - "automated"
  
  categories:
    - prefix: "Monoreason"
      default: "Monoreason: Large effort"
    - prefix: "Priority"
      default: "Priority: Medium"
    - prefix: "Team"
      default: "Team: Platform"
    
repository:
  local_path: "/tmp/dapulse"
  max_commits_behind: 100
  
linter:
  fix_command: "npm run eslint:changed:master"
  
logging:
  level: "INFO"
  directory: "logs"
```

## Use Cases

### Example 1: Developer sets their own Monoreason
```
PR labels: ["ci-plumber-to-merge", "Monoreason: Small effort"]
Result: Adds "workdays: Mon-Fri" only
Action: Skips Monoreason (already has one)
```

### Example 2: No Monoreason set
```
PR labels: ["ci-plumber-to-merge"]
Result: Adds "workdays: Mon-Fri" AND "Monoreason: Large effort"
Action: Adds default Monoreason
```

### Example 3: Multiple categories
```
PR labels: ["ci-plumber-to-merge", "Team: Backend"]
Result: Adds "workdays: Mon-Fri", "Monoreason: Large effort"
Action: Adds default Monoreason, skips Team (already has one)
```

## Adding New Label Categories

To add a new label category:

1. Edit `cfg/config.yaml`
2. Add to `categories` list:
   ```yaml
   - prefix: "YourCategory:"
     default: "YourCategory: Default Value"
   ```
3. Restart the service or run manually

No code changes needed!

