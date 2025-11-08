You are running the `/init` command to initialize the AI knowledge management system in a new project.

**Purpose**: Set up the `.ai/` knowledge base structure with your personal preferences and patterns.

**When to use**: Once at the start of each new project.

---

## Execution Steps

### Step 1: Check if Already Initialized

Check if `.ai/INDEX.md` already exists:

```bash
ls .ai/INDEX.md 2>/dev/null
```

**If it exists**:
- Ask user: "AI knowledge system already initialized. Reinitialize? (will preserve existing knowledge)"
- If yes, continue
- If no, abort

### Step 2: Create Directory Structure

Create all necessary directories:

```bash
mkdir -p .ai/context/decisions
mkdir -p .ai/knowledge/features
mkdir -p .ai/knowledge/components
mkdir -p .ai/knowledge/patterns
mkdir -p .ai/preferences
mkdir -p .claude/commands
```

**New directory**: `.ai/preferences/` - For cross-project personal preferences

### Step 3: Gather Project Information

Ask the user these questions (if not already known from context):

1. **Project name**: What is this project called?
2. **Project type**: (REST API, CLI tool, web app, mobile app, library, etc.)
3. **Tech stack**: What languages/frameworks? (e.g., "TypeScript/Node.js/Express")
4. **Purpose**: One sentence describing what this project does

### Step 4: Copy Personal Preferences

Copy your personal preferences from this repo to the new project:

**From**: `<agentic-workflows-repo>/.ai/preferences/`
**To**: `<new-project>/.ai/preferences/`

These files contain YOUR preferences that apply to ALL projects:
- Coding standards you always follow
- Error handling patterns you prefer
- Testing approaches you like
- Documentation styles you use
- Architecture principles you apply

**Note**: These are READ-ONLY references, not project-specific knowledge.

### Step 5: Create Core Files

Create these files with project-specific customization:

#### `.gitignore`

```gitignore
# AI Knowledge Base
.ai/sessions/

# Temporary files
*.tmp
*.temp
.DS_Store

# Editor files
.vscode/
.idea/
*.swp
*.swo
*~

# Dependencies (adjust based on tech stack)
node_modules/
__pycache__/
*.pyc

# Logs
*.log
```

#### `claude.md`

Use template but customize with:
- Project name from Step 3
- Project type from Step 3
- Tech stack from Step 3

#### `.ai/INDEX.md`

Initialize with:
- Project name
- Creation date
- Status: "Initialization"
- Knowledge counts: 0/0/0
- Recent Changes: "Initialized AI knowledge system"

#### `.ai/GUIDE.md`

Copy template (same for all projects)

#### `.ai/context/overview.md`

Customize with:
- Project name
- Project type
- Purpose statement from Step 3
- Tech stack

#### `.ai/context/architecture.md`

Create template based on project type:
- REST API → Include API architecture template
- CLI tool → Include CLI architecture template
- Web app → Include web app architecture template
- Custom → Generic template

### Step 6: Link Personal Preferences

Update `.ai/INDEX.md` to reference personal preferences:

Add section:
```markdown
## 🎨 Personal Preferences

This project follows these cross-project standards:

- [Coding Standards](./preferences/coding-standards.md)
- [Error Handling](./preferences/error-handling.md)
- [Testing Strategy](./preferences/testing-strategy.md)
- [Documentation Style](./preferences/documentation-style.md)

*These preferences apply to all your projects and are referenced, not modified.*
```

Update `claude.md` to mention preferences:
```markdown
### Personal Preferences

Before building, check `.ai/preferences/` for coding standards and patterns
that apply across all projects. Follow these unless project-specific needs
dictate otherwise.
```

### Step 7: Create Slash Commands

Copy command files to `.claude/commands/`:

**Essential commands**:
- `capture.md` - Knowledge capture workflow
- `init.md` - This file (for re-initialization or updates)

**Optional** (copy if they exist):
- `workflow.md` - Execute workflows
- `agent.md` - Activate agents
- `ask.md` - Query knowledge

### Step 8: Create Initial Decision (Optional)

If this is a greenfield project with tech stack decisions, create:

`.ai/context/decisions/001-initial-tech-stack.md`:

```markdown
---
type: decision
title: Initial Technology Stack Selection
status: accepted
date: YYYY-MM-DD
---

# Initial Technology Stack Selection

## Context

Starting new project: [Project Name]

## Decision

Using the following stack:
- [Tech stack from Step 3]

## Rationale

[Based on project requirements and personal preferences]

## Consequences

[Expected outcomes]
```

### Step 9: Validate Setup

Check that all files exist:

```bash
# Core files
ls claude.md
ls README.md
ls .gitignore

# AI knowledge structure
ls .ai/INDEX.md
ls .ai/GUIDE.md
ls .ai/context/overview.md
ls .ai/context/architecture.md

# Preferences (references)
ls .ai/preferences/*.md

# Commands
ls .claude/commands/capture.md
```

### Step 10: Git Configuration

If this is a git repository:

```bash
# Add knowledge files
git add .ai/ .claude/ claude.md .gitignore

# Don't commit yet - let user review first
```

Suggest to user:
```
Review the initialized files, then commit:
git commit -m "Initialize AI knowledge management system

- Set up .ai/ knowledge base structure
- Added personal preferences references
- Configured for [project type]"
```

### Step 11: Report to User

Provide summary:

```
✅ AI Knowledge Management System Initialized

**Project**: [Project Name]
**Type**: [Project Type]
**Tech Stack**: [Stack]

**Created:**
- .ai/INDEX.md - Knowledge base dashboard
- .ai/GUIDE.md - Navigation guide
- .ai/context/overview.md - Project description
- .ai/context/architecture.md - [Type] architecture template
- .ai/preferences/ - Your personal preferences (referenced)
- .claude/commands/capture.md - Knowledge capture workflow
- claude.md - AI entry point
- .gitignore - Configured for AI knowledge system

**Your Personal Preferences Loaded:**
- Coding Standards
- Error Handling Patterns
- Testing Strategy
- Documentation Style

**Next Steps:**
1. Review generated files in .ai/
2. Customize .ai/context/overview.md with project specifics
3. Customize .ai/context/architecture.md if needed
4. Commit: git add .ai .claude claude.md .gitignore && git commit -m "Initialize AI knowledge system"
5. Start building features!
6. After each feature: run /capture

**Ready to build!** 🚀
```

---

## Personal Preferences Structure

The `.ai/preferences/` directory should contain YOUR standards that apply to ALL projects:

**Example preferences to create** (in the agentic-workflows template repo):

### `.ai/preferences/coding-standards.md`

Your personal coding style:
- Naming conventions you prefer
- File organization patterns
- Code formatting rules
- Comment style

### `.ai/preferences/error-handling.md`

How you like to handle errors:
- Error handling patterns you use
- Logging approach
- Error message format
- Recovery strategies

### `.ai/preferences/testing-strategy.md`

Your testing philosophy:
- Test coverage targets
- Testing patterns (unit, integration, e2e)
- Mocking strategies
- Test file organization

### `.ai/preferences/documentation-style.md`

How you document code:
- Docstring format
- README structure
- API documentation approach
- Inline comment guidelines

---

## Important Distinctions

### Personal Preferences (.ai/preferences/)
- **Shared** across all projects
- **Referenced** (read-only) in each project
- Your general principles and standards
- Examples: "I always use constructor injection", "I prefer Jest for testing"

### Project Patterns (.ai/knowledge/patterns/)
- **Project-specific** implementations
- **Captured** via /capture as you build
- How preferences are applied in THIS project
- Examples: "How we implement auth in THIS API", "How we structure components in THIS app"

### Relationship

```
Personal Preference: "I use dependency injection"
    ↓
Project Pattern: "In this Express API, we use constructor injection with a DI container"
    ↓
Feature: "User authentication uses AuthService injected via container"
```

---

## Configuration for /init Command

The command needs to know where your template repo is. You have two options:

### Option 1: Hardcode in Command (Simple)

In `.claude/commands/init.md`, include:

```markdown
### Personal Preferences Source

Copy preferences from: `/path/to/agentic-workflows/.ai/preferences/`

Or if using remote:
```bash
curl -O https://raw.githubusercontent.com/yourusername/ai-knowledge-template/main/.ai/preferences/coding-standards.md
# ... etc
```
```

### Option 2: Environment Variable (Flexible)

Set once in your shell config:

```bash
# In ~/.bashrc or ~/.zshrc
export AI_TEMPLATE_REPO="/path/to/agentic-workflows"
```

Then in the init command, reference: `$AI_TEMPLATE_REPO/.ai/preferences/`

---

## Example: Personal Preferences Files

Let me create example preference files for you:
