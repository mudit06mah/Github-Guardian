# 🛡️ GitHub Guardian

**Secure your CI/CD pipelines by detecting security vulnerabilities in GitHub Actions workflows**

Guardian performs deep static analysis of GitHub Actions workflows to identify supply chain risks, insecure patterns, and potential security vulnerabilities **before** they reach production.

## Features

- **Deep Static Analysis**: Scans workflow YAML files for security issues
- **Severity Scoring**: Intelligent prioritization (critical, high, medium, low)
- **PR Comments**: Actionable feedback directly on pull requests
- **Check Runs**: Integration with GitHub's native check system
- **Configurable**: Customize thresholds and rules for your needs
- **Fast**: Analyzes workflows in seconds
- **Supply Chain Security**: Detects unpinned actions and risky dependencies

## What Guardian Detects

### High Severity Issues
- **Unpinned Actions**: Third-party actions not pinned to commit SHAs
- **Curl Pipe Shell**: Dangerous `curl | bash` patterns
- **Secret Exposure**: Secrets potentially leaked in logs
- **Excessive Permissions**: Overly broad `write-all` permissions

### Medium Severity Issues
- **Base64 Obfuscation**: Potentially obfuscated malicious code
- **Long Inline Scripts**: Scripts that should be external files (>200 chars)

### Low Severity Issues
- **Parse Errors**: Workflow files with syntax issues

## Quick Start

### Basic Usage

Add Guardian to your repository in `.github/workflows/guardian.yml`:

```yaml
name: Guardian Security Scan
on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  checks: write
  pull-requests: write

jobs:
  guardian:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Guardian
        uses: mudit06mah/github-guardian@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

That's it! Guardian will now scan all workflow changes in your pull requests.

## ⚙️ Configuration

### Action Inputs

| Input | Description | Default | Required |
|-------|-------------|---------|----------|
| `github_token` | GitHub token for API access | - | ✅ |
| `severity_threshold` | Minimum severity to report (`low`, `medium`, `high`, `critical`) | `medium` | ❌ |
| `fail_on_severity` | Fail check at this severity (`none`, `medium`, `high`, `critical`) | `high` | ❌ |
| `scan_mode` | Scan mode: `changed` or `all` | `changed` | ❌ |
| `config_path` | Path to custom config file | `.github/guardian.yml` | ❌ |

### Advanced Configuration

Create a `.github/guardian.yml` file for custom settings:

```yaml
# Minimum severity to show in reports
severity_threshold: medium

# Fail the check if this severity is found
fail_on_severity: high

# Ignore specific patterns (not yet implemented)
ignore:
  - "*.test.yml"
  
# Allowlist for specific actions
allowlist:
  actions:
    - "actions/checkout@v4"  # Well-known, trusted actions
```

### Example: Custom Thresholds

```yaml
- name: Run Guardian
  uses: mudit06mah/github-guardian@v1
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    severity_threshold: low        # Show all findings
    fail_on_severity: medium       # Fail on medium or high
    scan_mode: all                 # Scan all workflows, not just changed
```

## Output

Guardian provides:

1. **Check Run**: Native GitHub check with pass/fail status
2. **PR Comments**: Detailed findings with recommendations
3. **Annotations**: Inline annotations on workflow files
4. **Action Outputs**: Programmatic access to results

### Action Outputs

```yaml
- name: Run Guardian
  id: guardian
  uses: mudit06mah/github-guardian@v1
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}

- name: Check results
  run: |
    echo "Findings: ${{ steps.guardian.outputs.findings_count }}"
    echo "Highest severity: ${{ steps.guardian.outputs.highest_severity }}"
    echo "Passed: ${{ steps.guardian.outputs.check_passed }}"
```

## Development Setup
```bash
# Clone the repository
git clone https://github.com/mudit06mah/github-guardian.git
cd github-guardian

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Test locally
python analysis/main.py
```

## Authors

- **Aditya Bansal**
- **Mudit Maheshwari**
- **Sambhav Ghildiyal**

Under the guidance of **Dr. Pratik Srivastava**

---

**⭐ If Guardian helps secure your workflows, please star the repository!**
