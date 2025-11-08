---
type: decision
title: Personal Preferences System for Cross-Project Standards
status: accepted
date: 2025-11-08
---

# Personal Preferences System for Cross-Project Standards

## Context

When starting new projects, I want to maintain consistent coding standards, error handling patterns, testing strategies, and documentation styles across all my work. However, I also need to keep project-specific knowledge isolated to avoid polluting unrelated projects with irrelevant context.

### The Problem

**Without a preference system:**
- ❌ Each new project starts from scratch with no standards
- ❌ AI assistants don't know my preferred approaches
- ❌ Inconsistent patterns across projects
- ❌ Have to re-explain preferences every time
- ❌ Or, copying `.ai/knowledge/` pollutes context with unrelated project details

### Requirements

1. **Share personal standards** across all projects
2. **Keep project knowledge isolated** (no cross-contamination)
3. **Easy initialization** for new projects
4. **AI-friendly** - AI can reference preferences automatically
5. **Tool-agnostic** - Works with any AI assistant

## Decision

We will implement a **three-tier knowledge system**:

### Tier 1: Template Structure
**What**: Directory structure, command files, navigation guides
**Scope**: Shared across all projects
**Location**: Template repository (`ai-knowledge-template`)
**Example**: `.ai/` directories, `.claude/commands/capture.md`, `GUIDE.md`

### Tier 2: Personal Preferences (NEW)
**What**: Cross-project coding standards, patterns, philosophies
**Scope**: Referenced (read-only) in all projects
**Location**: `.ai/preferences/` in both template and each project
**Example**: Coding standards, error handling patterns, testing strategy

### Tier 3: Project Knowledge
**What**: Project-specific features, components, patterns
**Scope**: Isolated per project
**Location**: `.ai/knowledge/` (grows via `/capture`)
**Example**: "How authentication works in THIS API"

### Preference Files Created

```
.ai/preferences/
├── coding-standards.md      # Naming, organization, quality principles
├── error-handling.md        # Error patterns, logging, retry strategies
├── testing-strategy.md      # Test philosophy, coverage, patterns
└── documentation-style.md   # Docs philosophy, formats, examples
```

## Implementation

### Template Repository Setup

1. Create preference files in template repo
2. Each new project gets a copy of preferences
3. Preferences are **referenced, not modified**
4. Updates to preferences propagate via template updates

### `/init` Command

Created `.claude/commands/init.md` that:

1. Creates directory structure
2. Copies preference files from template
3. Customizes project-specific files (claude.md, overview.md)
4. Links to preferences in INDEX.md
5. Sets up slash commands

### How AI Uses Preferences

#### In `claude.md`:
```markdown
### Personal Preferences

Before building, check `.ai/preferences/` for coding standards and patterns
that apply across all projects. Follow these unless project-specific needs
dictate otherwise.
```

#### In `.ai/INDEX.md`:
```markdown
## 🎨 Personal Preferences

This project follows these cross-project standards:
- [Coding Standards](./preferences/coding-standards.md)
- [Error Handling](./preferences/error-handling.md)
- [Testing Strategy](./preferences/testing-strategy.md)
- [Documentation Style](./preferences/documentation-style.md)
```

#### Workflow:
1. AI reads `claude.md`
2. Sees mention of preferences
3. Reads `.ai/preferences/` before building
4. Applies standards to new code
5. Documents project-specific patterns in `.ai/knowledge/patterns/`

### Relationship: Preferences vs. Patterns

```
Personal Preference (.ai/preferences/error-handling.md):
  "I use custom error classes with context"
  ↓
Project Pattern (.ai/knowledge/patterns/error-handling.md):
  "In this Express API, we use these 6 error classes"
  ↓
Feature (.ai/knowledge/features/authentication.md):
  "Auth throws AuthenticationError on invalid token"
```

**Key distinction**:
- **Preferences**: General principles ("I prefer X")
- **Patterns**: Project implementation ("We implement X like this")
- **Features**: Specific usage ("Feature Y uses pattern X")

## Rationale

### Why This Approach?

**Pros:**
- ✅ Consistent standards across projects
- ✅ No cross-project knowledge pollution
- ✅ AI learns my preferences once, applies everywhere
- ✅ Easy to update preferences (change template, propagate)
- ✅ Preferences evolve separately from project knowledge
- ✅ Tool-agnostic (works with any AI assistant)

**Cons:**
- ❌ Need to copy preference files to each project
- ❌ Updates to preferences don't auto-propagate to existing projects

**Mitigations:**
- Preference copies are small (4 markdown files)
- Can manually update preferences in existing projects when needed
- Most preferences change infrequently

### Alternatives Considered

#### Alternative 1: Global Preferences Repository

**Approach**: One shared preferences repo, symlink from each project

**Rejected because:**
- Symlinks don't work well across systems
- Breaks portability (can't share project without preference repo)
- AI would need to know where to find external repo

#### Alternative 2: Include Preferences in Each Project's Knowledge

**Approach**: Document preferences in each project's `.ai/knowledge/patterns/`

**Rejected because:**
- Duplicates documentation across projects
- Inconsistent as preferences evolve
- Mixes personal preferences with project patterns

#### Alternative 3: Hard-code Preferences in `claude.md`

**Approach**: Write all preferences directly in `claude.md` for each project

**Rejected because:**
- Makes `claude.md` huge and hard to maintain
- Still duplicates content across projects
- Not modular or scannable

## Consequences

### Positive

1. **Consistency**: All projects follow same standards
2. **Efficiency**: AI doesn't need to ask about preferences
3. **Quality**: Standards are documented and referenced
4. **Onboarding**: New projects start with best practices
5. **Evolution**: Can improve preferences in template, propagate to new projects

### Negative

1. **Copying**: Each project has a copy of preference files
2. **Sync**: Updates don't auto-propagate to existing projects
3. **Overhead**: Need to maintain preference files in template

### Neutral

1. **Size**: Adds ~4 markdown files per project (~20KB total)
2. **Complexity**: Introduces third tier (but improves organization)

## Usage

### Starting a New Project

```bash
# Clone template or run:
/init

# AI sets up:
# - Directory structure
# - Personal preferences (copied)
# - Project-specific files (customized)
# - Slash commands
```

### Referencing Preferences

**In code reviews:**
> "This should follow the error handling pattern in `.ai/preferences/error-handling.md`"

**When building:**
> AI: "I see you prefer constructor injection (from coding-standards.md), implementing accordingly"

**When documenting:**
> "Documented in `.ai/knowledge/patterns/error-handling.md` - extends the preference from `.ai/preferences/error-handling.md`"

### Updating Preferences

**For one project:**
```bash
# Edit preference files
vim .ai/preferences/coding-standards.md

# Commit
git commit -m "Update coding standards preference"
```

**For all future projects:**
```bash
# Update template repo
cd ai-knowledge-template
vim .ai/preferences/coding-standards.md

git commit -m "Update coding standards preference"
git push

# New projects get updated preferences via /init
```

## Follow-up Actions

- [x] Create 4 preference files
- [x] Implement `/init` command
- [x] Update `claude.md` to reference preferences
- [x] Update `INDEX.md` to link preferences
- [x] Document this decision in ADR
- [ ] Test `/init` in a new project
- [ ] Refine preference files based on usage

## Success Metrics

1. **Consistency**: New projects follow same patterns
2. **Efficiency**: AI references preferences without asking
3. **Quality**: Code reviews reference documented standards
4. **Adoption**: `/init` used for all new projects

## Related

- [Architecture](../architecture.md) - System architecture overview
- [Preferences](../../preferences/) - The preference files themselves
- [GUIDE.md](../../GUIDE.md) - How to navigate knowledge base

---

**Status**: Accepted
**Date**: 2025-11-08
**Author**: System Designer
