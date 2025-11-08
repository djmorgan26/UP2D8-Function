# Navigation Guide - Where to Look

**Purpose**: This guide helps you find information quickly without searching the entire repository.

**When to use this**: Whenever you need to find specific information about this project.

---

## Common Questions → Where to Find Answers

### "What does this project do?"
**→** Read [context/overview.md](./context/overview.md)

### "How is the system architected?"
**→** Read [context/architecture.md](./context/architecture.md)

### "Why was [decision] made?"
**→** Check [context/decisions/](./context/decisions/) for Architecture Decision Records (ADRs)
**→** If empty, the decision might be documented in the relevant feature/component file

### "How does [feature] work?"
**→** Check [knowledge/features/[feature-name].md](./knowledge/features/)
**→** If not found: Knowledge hasn't been captured yet, search codebase and then run `/capture`

### "What components exist?"
**→** Browse [knowledge/components/](./knowledge/components/)
**→** Check [INDEX.md](./INDEX.md) for quick list

### "What coding patterns are used here?"
**→** Browse [knowledge/patterns/](./knowledge/patterns/)
**→** Check [architecture.md](./context/architecture.md) for pattern overview

### "What changed recently?"
**→** Read [INDEX.md](./INDEX.md) → "Recent Changes" section

### "How do I [add a feature / fix a bug / etc.]?"
**→** Check [knowledge/patterns/](./knowledge/patterns/) for established processes
**→** If first time doing this task: Build it, then run `/capture` to document the process

### "What should I know before starting work?"
**→** Read [INDEX.md](./INDEX.md) → Recent Changes
**→** Read relevant feature docs in [knowledge/features/](./knowledge/features/)
**→** Review [knowledge/patterns/](./knowledge/patterns/) for consistency

### "Where do I document [my work]?"
**→** Run `/capture` after completing work
**→** AI will analyze changes and create/update appropriate documentation

---

## When Knowledge Doesn't Exist Yet

**This knowledge base grows over time.** If you can't find something:

1. **Search the codebase** for what you need (as a fallback)
2. **Build the feature** or fix the bug
3. **Run `/capture`** to document what you learned
4. **Next time**: The knowledge will be here

**Philosophy**: Start simple, build incrementally, capture knowledge as you go.

---

## Decision Tree - Where to Look

```
Need information?
│
├─ About project purpose/goals?
│  └─ Read .ai/context/overview.md
│
├─ About architecture/structure?
│  └─ Read .ai/context/architecture.md
│
├─ About a specific feature?
│  ├─ Check .ai/knowledge/features/[feature-name].md
│  └─ If not found: Knowledge not captured yet
│
├─ About a component/module?
│  ├─ Check .ai/knowledge/components/[component-name].md
│  └─ If not found: Knowledge not captured yet
│
├─ About how to do something (patterns/processes)?
│  ├─ Check .ai/knowledge/patterns/
│  └─ If not found: Build it, then /capture
│
├─ About why something was decided?
│  ├─ Check .ai/context/decisions/NNN-decision-name.md
│  └─ If not found: May be inline in feature/component docs
│
└─ Recent changes?
   └─ Check .ai/INDEX.md → Recent Changes
```

---

## File Naming Conventions

**Follow these conventions when creating new knowledge files:**

### Features
- **Location**: `.ai/knowledge/features/`
- **Format**: `feature-name.md` (kebab-case)
- **Examples**:
  - `user-authentication.md`
  - `password-reset.md`
  - `email-notifications.md`

### Components
- **Location**: `.ai/knowledge/components/`
- **Format**: `component-name.md` (kebab-case)
- **Examples**:
  - `api-gateway.md`
  - `database-layer.md`
  - `auth-middleware.md`

### Patterns
- **Location**: `.ai/knowledge/patterns/`
- **Format**: `pattern-name.md` (kebab-case)
- **Examples**:
  - `error-handling.md`
  - `dependency-injection.md`
  - `repository-pattern.md`

### Decisions (ADRs)
- **Location**: `.ai/context/decisions/`
- **Format**: `NNN-short-title.md` (numbered, kebab-case)
- **Examples**:
  - `001-choice-of-framework.md`
  - `002-database-selection.md`
  - `003-jwt-vs-sessions.md`

**Note**: The `/capture` command follows these conventions automatically.

---

## Information Architecture

### Layer 1: Context (Stable)
**Location**: `.ai/context/`
**Changes**: Infrequently
**Contains**: Project overview, architecture, major decisions
**Read when**: Starting on the project or making architectural changes

### Layer 2: Knowledge (Growing)
**Location**: `.ai/knowledge/`
**Changes**: Frequently (every feature)
**Contains**: Features, components, patterns as they're built
**Read when**: Before building related features or to understand existing code

### Layer 3: Navigation (Helper)
**Location**: `.ai/INDEX.md`, `.ai/GUIDE.md`
**Changes**: Updated automatically by `/capture`
**Contains**: Recent changes, navigation help, knowledge map
**Read when**: Every session start, when you need to find something

---

## Quick Reference Table

| Question Type | Where to Look | Empty? |
|--------------|---------------|--------|
| What/Why (Project) | `.ai/context/overview.md` | ✅ No |
| How (Architecture) | `.ai/context/architecture.md` | ✅ No |
| How (Feature) | `.ai/knowledge/features/` | ⏳ Grows over time |
| How (Component) | `.ai/knowledge/components/` | ⏳ Grows over time |
| How (Process) | `.ai/knowledge/patterns/` | ⏳ Grows over time |
| Why (Decision) | `.ai/context/decisions/` | ⏳ Grows over time |
| What's new? | `.ai/INDEX.md` | ✅ No |

---

## Best Practices

### Before Building
1. **Check INDEX.md** for recent changes that might affect your work
2. **Review similar features** in `knowledge/features/` to follow patterns
3. **Check patterns** in `knowledge/patterns/` to maintain consistency

### While Building
1. **Take mental notes** of key decisions and patterns you're using
2. **Note any new patterns** you're introducing
3. **Consider architectural decisions** that should be documented

### After Building
1. **Run `/capture`** to automatically document your work
2. **Review generated docs** to ensure they're accurate
3. **Update if needed** - the `/capture` command creates drafts, you can refine them

---

## Tips for Efficient Navigation

✅ **DO**:
- Start with INDEX.md to see what's new
- Use this GUIDE when you don't know where to look
- Follow file naming conventions
- Run `/capture` after completing work

❌ **DON'T**:
- Search the entire repository without checking knowledge base first
- Create knowledge files manually (use `/capture`)
- Ignore existing patterns in `knowledge/patterns/`
- Skip reading Recent Changes in INDEX.md

---

## This Guide Will Evolve

As the project grows, this guide will be updated with:
- New question patterns you commonly ask
- Additional navigation shortcuts
- Links to frequently accessed knowledge
- Lessons learned about finding information efficiently

**Last Updated**: 2025-11-08 (Foundation)
