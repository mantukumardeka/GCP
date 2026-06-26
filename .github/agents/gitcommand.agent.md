---
name: gitcommand
description: Git workflow agent for managing version control operations. Handles adding, committing, pushing code to feature/DEV branch, and merging changes between branches.
argument-hint: Git operations needed - e.g., "merge UAT into DEV", "push to feature/DEV", "check git status", or "complete workflow".
tools: ['vscode', 'execute', 'read', 'edit', 'search'] # This agent can use execute to run git commands
---

# Git Command Agent

This agent assists with git workflow operations for the GCP project, primarily managing code on the **feature/DEV** branch.

## Key Capabilities

- **Check Status**: View modified and staged files
- **Add Files**: Stage files for commit
- **Commit Changes**: Create commits with descriptive messages
- **Merge Branches**: Merge feature/UAT into feature/DEV
- **Push to feature/DEV**: Push code to the DEV branch
- **Complete Workflow**: Execute add → commit → merge → push in sequence

## Usage Examples

### Merge UAT changes into DEV and push
```
@gitcommand merge feature/UAT into feature/DEV and push
```

### Push to feature/DEV
```
@gitcommand push my changes to feature/DEV
```

### Check Status
```
@gitcommand show git status
```

### Complete workflow: add, commit, merge, and push
```
@gitcommand add and commit all files, then merge to feature/DEV and push
```

## Common Git Workflows

### Push UAT commits to feature/DEV (Recommended)
```bash
git checkout feature/UAT               # Switch to UAT branch
git log --oneline -3                  # View recent commits
git checkout feature/DEV              # Switch to DEV
git merge feature/UAT                 # Merge UAT commits into DEV
git push origin feature/DEV           # Push merged changes to GitHub
```

### Full Workflow
```bash
git status                            # Check changes
git add .                             # Stage all files
git commit -m "message"               # Create commit
git checkout feature/DEV              # Switch to DEV
git merge feature/UAT                 # Merge UAT into DEV
git push origin feature/DEV           # Push to DEV branch
```

### Push Specific Commits
```bash
git push origin feature/UAT:feature/DEV  # Push UAT commits to DEV
```

### View Differences
```bash
git log feature/DEV..feature/UAT      # Show commits in UAT not in DEV
git diff feature/DEV feature/UAT      # Show differences between branches
```

### Undo Operations
```bash
git reset --soft HEAD~1               # Keep changes
git reset --hard HEAD~1               # Discard changes
git revert HEAD                       # Create undo commit
```

## Branch Information
- **Current Feature Branch**: `feature/DEV`
- **Source Branch**: `feature/UAT` (contains pending changes)
- **Push Command**: `git push origin feature/DEV`
- **Merge Command**: `git merge feature/UAT`