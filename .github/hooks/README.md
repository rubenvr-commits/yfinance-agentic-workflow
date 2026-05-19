# Pre-Commit Test Runner Hook

This hook automatically validates code quality before commits by checking if Python files have corresponding tests.

## Components

### 1. Agent Hook (Automatic)
- **File**: `.github/hooks/pre-commit-validator.json`
- **Trigger**: PreToolUse (when agent executes commands)
- **Behavior**: Detects staged Python files and asks user to validate with Q&A Tester if no tests found
- **Scope**: Team-shared, enabled automatically for all developers

### 2. Git Pre-Commit Hook (Manual Installation)
- **File**: `.github/scripts/git-pre-commit`
- **When**: Before local git commits
- **Behavior**: Lists Python files without tests and prompts to continue or abort

## Installation

### For Agent Hook (Automatic)
No installation needed - the hook in `.github/hooks/pre-commit-validator.json` is auto-loaded by VS Code agent.

### For Git Pre-Commit Hook (Optional)
Run this command once to install:

```bash
# On Linux/macOS
cp .github/scripts/git-pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# On Windows (Git Bash or WSL)
cp .github/scripts/git-pre-commit .git/hooks/pre-commit
```

Or manually:
1. Copy `.github/scripts/git-pre-commit` content
2. Create `.git/hooks/pre-commit` file
3. Paste content and make executable

## Workflow

### With Agent Hook
```
Developer: "Commit changes"
Agent: Detects staged Python files
Agent: Checks for test files
Agent: If missing tests → "Run Q&A Tester to validate?"
Developer: Yes → Agent calls Q&A Tester
Developer: Tests pass → Commit proceeds
```

### With Git Pre-Commit Hook
```bash
git add src/new_feature.py
git commit -m "Add feature"
# Hook runs: "No tests for new_feature.py - Continue? (y/n)"
# Developer: y (or create tests first)
# Commit proceeds
```

## Test File Detection

The hook recognizes these test patterns:

```
src/my_module.py    →  tests/test_my_module.py
src/my_module.py    →  src/test_my_module.py
src/my_module.py    →  src/my_module_test.py
src/my_module.py    →  __tests__/my_module.test.py
```

## Integration with Q&A Tester

When the agent hook detects missing tests, it offers to run Q&A Tester automatically:

```
@q-a-tester validate src/my_module.py with these requirements:
[requirements from the agent analysis]
```

## Troubleshooting

**Hook not triggering?**
- Ensure `.github/hooks/pre-commit-validator.json` exists
- Restart VS Code or reload agent customizations

**Git hook not executing?**
- Check file permissions: `chmod +x .git/hooks/pre-commit`
- Verify path: `ls -la .git/hooks/`

**False positives (tests not detected)?**
- Update test file patterns in `.github/scripts/validate_pre_commit.py`
- Ensure test files are in recognized locations

## Bypass (Emergency Only)

```bash
# Skip agent hook (not recommended)
# Manually create commit via terminal without going through agent

# Skip git pre-commit hook
git commit -m "message" --no-verify
```
