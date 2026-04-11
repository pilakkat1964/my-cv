# Development Workflow Guide

## Overview

The `./tools/dev.py` script provides a unified interface for all development and git branching operations. It ensures proper Ruby version management via mise and handles both feature development and bugfixes through standardized branching.

## Quick Start

### First Time Setup
```bash
cd /path/to/cv
./tools/dev.py setup
```

### Daily Development
```bash
# Start a feature branch
./tools/dev.py feature add-dark-mode

# Make changes to files...

# Commit your work
./tools/dev.py commit -m "feat: Add dark mode support"

# Test everything before merging
./tools/dev.py test

# Merge back to main
./tools/dev.py merge
```

## Detailed Command Reference

### Setup & Environment

#### `./tools/dev.py setup`
Configures the development environment on first run:
- Verifies mise is installed
- Checks Ruby version from mise.toml
- Installs/updates tools via mise
- Installs Ruby gems locally

**When to use:** 
- Initial project setup
- After major dependency changes
- When gems seem outdated

---

### Jekyll Development

#### `./tools/dev.py serve [--host HOST]`
Start local Jekyll dev server with auto-reload

```bash
./tools/dev.py serve                 # Default: 127.0.0.1:4000
./tools/dev.py serve --host 0.0.0.0  # Listen on all interfaces
```

**Features:**
- Auto-activates correct Ruby version via mise
- Auto-reload on file changes
- Detects Docker and enables force_polling if needed

---

#### `./tools/dev.py build [--production]`
Clean build the site for testing/deployment

```bash
./tools/dev.py build                # Development build
./tools/dev.py build --production   # Production build with optimizations
```

**What it does:**
1. Cleans `.jekyll-cache` and `_site` directories
2. Rebuilds from scratch
3. Sets `JEKYLL_ENV` appropriately

---

#### `./tools/dev.py test`
Full testing: Build + validate with htmlproofer

```bash
./tools/dev.py test
```

**What it does:**
1. Builds in production mode
2. Validates all internal links
3. Reports any broken links or issues

**Before pushing:** Always run this to catch link issues

---

#### `./tools/dev.py check [--dry-run] [--htmlproofer]`
Check and fix broken internal links in posts

```bash
./tools/dev.py check                      # Check only
./tools/dev.py check --dry-run           # Show what would be fixed
./tools/dev.py check --htmlproofer       # Check + build + full test
```

**What it does:**
1. Scans published posts for internal `/posts/` links
2. Identifies links to draft/unpublished posts
3. Can auto-fix by marking as "(coming soon)"

---

### Branch Management

#### `./tools/dev.py feature <name>`
Create and switch to a feature branch

```bash
./tools/dev.py feature add-dark-mode
./tools/dev.py feature update-resume-2025
```

**What it does:**
1. Fetches latest from origin
2. Creates `feature/<name>` branch from main
3. Switches to the new branch
4. Ready for you to make changes

**Naming convention:** Use hyphens, keep it short and descriptive

---

#### `./tools/dev.py bugfix <name>`
Create and switch to a bugfix branch

```bash
./tools/dev.py bugfix fix-link-colors
./tools/dev.py bugfix typo-in-bio
```

**What it does:**
1. Fetches latest from origin
2. Creates `bugfix/<name>` branch from main
3. Switches to the new branch
4. Ready for you to make changes

**Naming convention:** Describe the bug being fixed

---

#### `./tools/dev.py switch <branch>`
Switch to an existing branch

```bash
./tools/dev.py switch dev
./tools/dev.py switch feature/dark-mode
./tools/dev.py switch master
```

**Features:**
- Auto-completes if branch exists
- Shows error if branch not found
- Displays working directory status

---

#### `./tools/dev.py commit -m "message"`
Commit all changes with a message

```bash
./tools/dev.py commit -m "feat: Add dark mode support"
./tools/dev.py commit -m "docs: Update README"
./tools/dev.py commit -m "fix: Resolve CSS issue on mobile"
```

**What it does:**
1. Stages all changes (`git add -A`)
2. Creates commit with your message
3. Shows commit hash and message

**Commit message format:**
- Start with type: `feat`, `fix`, `docs`, `test`, `chore`
- Follow with brief description
- Use present tense: "Add feature" not "Added feature"

---

#### `./tools/dev.py merge`
Merge current branch back to main and push

```bash
./tools/dev.py merge
```

**What it does:**
1. Verifies no uncommitted changes
2. Fetches latest from origin
3. Switches to main branch
4. Merges feature/bugfix branch
5. Pushes to origin
6. Provides cleanup instructions

**Safety checks:**
- Won't merge if working directory has uncommitted changes
- Detects merge conflicts and guides resolution
- Prevents merging into main directly

**After merge:**
```bash
# Delete the merged branch
git branch -d feature/dark-mode
```

---

#### `./tools/dev.py delete <branch>`
Delete a local branch

```bash
./tools/dev.py delete feature/old-feature
./tools/dev.py delete bugfix/already-fixed
./tools/dev.py delete -f feature/mistake    # Force delete
```

**Options:**
- `-f, --force`: Use `-D` instead of `-d` for unmerged branches

**Safety:**
- Won't delete main/master
- Switches away from branch if currently on it

---

#### `./tools/dev.py status`
Show current branch and repository status

```bash
./tools/dev.py status
```

**Displays:**
- Current branch name
- All local branches with tracking info
- Working directory status
- Uncommitted changes

---

## Typical Workflows

### Feature Development Workflow

```bash
# 1. Start feature
./tools/dev.py feature add-contact-form

# 2. Make changes, test locally
./tools/dev.py serve
# Edit files, view at http://127.0.0.1:4000/cv/

# 3. Commit your changes
./tools/dev.py commit -m "feat: Add contact form to home page"

# 4. Make more changes if needed
# ./tools/dev.py commit -m "feat: Add form validation"

# 5. Full testing before merge
./tools/dev.py test

# 6. Merge back to main
./tools/dev.py merge

# 7. Clean up (optional)
git branch -d feature/add-contact-form
```

---

### Bug Fix Workflow

```bash
# 1. Start bugfix
./tools/dev.py bugfix fix-mobile-layout

# 2. Make fix and test
./tools/dev.py serve
# Test on mobile...

# 3. Commit fix
./tools/dev.py commit -m "fix: Correct responsive layout on small screens"

# 4. Verify links still work
./tools/dev.py test

# 5. Merge
./tools/dev.py merge

# 6. Delete branch
git branch -d bugfix/fix-mobile-layout
```

---

### Switching Between Tasks

```bash
# Currently on feature/add-form

# Switch to bugfix
./tools/dev.py switch bugfix/fix-typo

# Make fix and commit
./tools/dev.py commit -m "fix: Correct typo in bio"

# Switch back to feature
./tools/dev.py switch feature/add-form

# Continue working
```

---

## Branch Naming Conventions

### Feature Branches
```
feature/add-dark-mode
feature/update-portfolio
feature/responsive-design
```

### Bugfix Branches
```
bugfix/fix-link-colors
bugfix/typo-in-bio
bugfix/mobile-layout-issue
```

### Development Branch (special)
```
dev   # Used for testing before deploying to master
```

---

## Important Notes

### Ruby Version Management

All commands automatically activate mise with Ruby 3.4.9. If you get version mismatch errors:
```bash
# Make sure your shell is using mise
eval "$(mise activate bash)"

# Or run setup again
./tools/dev.py setup
```

### Main/Master Branch Detection

The script automatically detects whether your repo uses `main` (GitHub) or `master` (older repos):
- Feature/bugfix branches are created from the correct main branch
- Merges target the correct main branch
- Works seamlessly with both naming conventions

### Safety Features

✅ Won't delete main/master branches
✅ Detects uncommitted changes before merge
✅ Checks for merge conflicts
✅ Verifies Ruby version before running Jekyll
✅ Warns before committing directly to main

### Commit Message Guidelines

Use conventional commits for consistency:

```
feat:   New feature
fix:    Bug fix
docs:   Documentation changes
test:   Test additions/modifications
chore:  Build, deps, tooling
refactor: Code reorganization
perf:   Performance improvements
```

Example:
```bash
./tools/dev.py commit -m "feat: Add search functionality"
./tools/dev.py commit -m "fix: Resolve CSS overflow issue"
./tools/dev.py commit -m "docs: Update installation guide"
```

---

## Troubleshooting

### "Ruby version mismatch"
```bash
# Activate mise in current shell
eval "$(mise activate bash)"

# Run setup again
./tools/dev.py setup
```

### "Merge conflict detected"
1. Resolve conflicts manually in affected files
2. Commit the resolution: `./tools/dev.py commit -m "fix: Resolve merge conflicts"`
3. Push: `git push origin master`

### "Branch does not exist"
```bash
# List all branches
git branch -a

# Create it with feature/bugfix command
./tools/dev.py feature new-feature-name
```

### Jekyll won't start
1. Verify setup: `./tools/dev.py setup`
2. Check if port 4000 is in use: `lsof -i :4000`
3. Try different port: `./tools/dev.py serve --host 127.0.0.1`

---

## Quick Reference Card

| Command | Purpose |
|---------|---------|
| `setup` | Configure environment |
| `serve` | Start dev server |
| `build` | Build site |
| `test` | Build + test |
| `check` | Check internal links |
| `feature <name>` | Start feature branch |
| `bugfix <name>` | Start bugfix branch |
| `switch <branch>` | Switch branch |
| `commit -m "msg"` | Commit changes |
| `merge` | Merge to main |
| `delete <branch>` | Delete branch |
| `status` | Show status |

---

## Next Steps

1. Run `./tools/dev.py setup` for first-time setup
2. Create a feature branch: `./tools/dev.py feature your-feature-name`
3. Make changes and commit: `./tools/dev.py commit -m "your message"`
4. Test everything: `./tools/dev.py test`
5. Merge back: `./tools/dev.py merge`

Happy developing! 🚀
