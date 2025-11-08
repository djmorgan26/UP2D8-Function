# System Architecture

**Last Updated**: 2025-11-08
**Status**: Foundation Phase
**Version**: 1.0

---

## Overview

This is a **file-based knowledge management system** with a layered architecture designed for progressive context discovery. AI assistants navigate from general (project overview) to specific (individual features) through a structured hierarchy.

### Core Concept

```
Entry Point (claude.md)
    ↓
Dashboard (INDEX.md) ← Shows what's new
    ↓
Navigation (GUIDE.md) ← Shows where to look
    ↓
Knowledge (specific files) ← Feature/component details
    ↓
Code (actual implementation) ← Referenced from knowledge
```

---

## System Layers

### Layer 1: Entry & Orientation

**File**: `claude.md`
**Purpose**: AI reads this FIRST, every session
**Contents**:
- Project overview
- How to navigate the knowledge base
- Available commands
- Quick reference table

**Why separate from README.md?**
- README.md is for humans
- claude.md is optimized for AI parsing
- Different audiences, different needs

### Layer 2: Dashboard & Navigation

**Files**: `.ai/INDEX.md`, `.ai/GUIDE.md`

#### INDEX.md (Dashboard)
- Recent changes (most important!)
- Knowledge map (what exists)
- Project stats
- Current focus
- Quick links

#### GUIDE.md (Navigation)
- Question → Answer mapping
- Decision trees
- File naming conventions
- Best practices

**Navigation Flow**:
```
"How does auth work?"
    → Check GUIDE.md
    → Directed to knowledge/features/authentication.md
    → Find answer quickly
```

### Layer 3: Context (Stable Information)

**Location**: `.ai/context/`
**Update Frequency**: Rarely (only when architecture changes)

**Files**:
- `overview.md` - What the project does, why it exists
- `architecture.md` - This file, how the system works
- `decisions/` - Architecture Decision Records (ADRs)

**Purpose**: Foundational knowledge that changes infrequently

### Layer 4: Knowledge (Growing Information)

**Location**: `.ai/knowledge/`
**Update Frequency**: With every feature (frequently)

**Subdirectories**:

- **`features/`** - Feature-level documentation
  - What the feature does
  - How it works
  - Key decisions made
  - Usage examples
  - Testing approach

- **`components/`** - Component/module documentation
  - Component purpose
  - API/interface
  - Dependencies
  - Integration points

- **`patterns/`** - Coding patterns used in this project
  - Error handling patterns
  - Testing patterns
  - Architecture patterns (DI, factories, etc.)
  - Project-specific conventions

**Growth Pattern**:
```
Day 1:   Empty directories
Week 1:  2-3 features documented
Month 1: 10+ features, patterns emerging
Month 3: Comprehensive knowledge base
```

### Layer 5: Automation

**Location**: `.claude/commands/`
**Purpose**: Slash commands for Claude Code

**Current**:
- `capture.md` - Knowledge capture workflow

**Future** (only if needed):
- `workflow.md` - Execute standard workflows
- `agent.md` - Activate specialized agents
- `ask.md` - Query knowledge base

---

## File Structure

```
agentic-workflows/
│
├── claude.md                          # Entry point for AI
├── README.md                          # Entry point for humans
├── .gitignore                         # Ignore temp files
│
├── .ai/                               # AI knowledge base
│   ├── INDEX.md                       # Dashboard - start here
│   ├── GUIDE.md                       # Navigation helper
│   │
│   ├── context/                       # Stable context
│   │   ├── overview.md                # Project description
│   │   ├── architecture.md            # This file
│   │   └── decisions/                 # ADRs
│   │       └── 001-example.md
│   │
│   └── knowledge/                     # Growing knowledge
│       ├── features/                  # Feature docs
│       │   └── feature-name.md
│       ├── components/                # Component docs
│       │   └── component-name.md
│       └── patterns/                  # Pattern docs
│           └── pattern-name.md
│
└── .claude/                           # Claude Code specific
    └── commands/                      # Slash commands
        └── capture.md                 # /capture command
```

---

## Knowledge Capture Flow

### The `/capture` Command

**Purpose**: Automatically generate documentation from git changes

**Trigger**: User runs `/capture` after completing work

**Process**:

```
1. Analyze Changes
   ├─> git diff HEAD (or last commit)
   ├─> Identify modified/new files
   └─> Extract functions/classes changed

2. Understand Context
   ├─> Read changed files
   ├─> Parse commit messages
   └─> Identify patterns used

3. Determine Type
   ├─> New feature? → Create feature doc
   ├─> New component? → Create component doc
   ├─> New pattern? → Create pattern doc
   └─> Major decision? → Create ADR

4. Generate Documentation
   ├─> Use standard template
   ├─> Add YAML frontmatter
   ├─> Include file references
   ├─> Link related knowledge
   └─> Write clear explanations

5. Update INDEX.md
   ├─> Add to Recent Changes
   ├─> Update knowledge counts
   └─> Add cross-references

6. Validate
   ├─> Check file references exist
   ├─> Validate YAML frontmatter
   └─> Ensure links work
```

**Output**: New or updated knowledge files + updated INDEX.md

### Knowledge File Format

Every knowledge file uses this structure:

```markdown
---
type: feature | component | pattern
name: Human-Readable Name
status: implemented | in-progress | planned | deprecated
created: YYYY-MM-DD
updated: YYYY-MM-DD
files:
  - path/to/file.ext
related:
  - .ai/knowledge/related/doc.md
tags: [tag1, tag2]
---

# Feature/Component Name

## What It Does
[Brief description]

## How It Works
[Detailed explanation with code references]

## Key Decisions
[Important choices made]

## Usage Examples
[Code examples]

## Testing
[Test approach and coverage]

## Common Issues
[Known issues and solutions]

## Future Ideas
[Potential improvements]
```

---

## Design Decisions

### Why File-Based?

**Pros**:
- ✅ Git-native (version control, diffs, merges)
- ✅ Human-readable (markdown)
- ✅ No database setup required
- ✅ Works offline
- ✅ Portable across systems
- ✅ Greppable, searchable with standard tools

**Cons**:
- ❌ No complex queries (acceptable for this use case)
- ❌ Manual reference management (solved by `/capture`)

**Decision**: File-based wins for simplicity and git integration.

### Why Markdown + YAML?

**Markdown**:
- Human-readable
- Widely supported
- Git-friendly
- AI assistants parse it natively

**YAML Frontmatter**:
- Structured metadata
- Easy to parse
- Standard convention
- Extensible

**Alternative Considered**: JSON files
**Rejected Because**: Less human-readable, harder to write/edit

### Why Layered Architecture?

**Progressive Disclosure**: AI gets more specific context as it navigates deeper
**Separation of Concerns**: Stable context vs. growing knowledge
**Scalability**: Easy to find information as knowledge base grows
**Performance**: AI reads only what it needs

### Why `.ai/` Directory?

**Alternatives Considered**:
- `.knowledge/` - Too generic
- `.docs/` - Conflicts with human documentation
- `.agentic/` - Too specific to one paradigm
- `.ai/` - **CHOSEN**: Short, clear, indicates AI-specific content

### Why Tool-Agnostic Design?

**Problem**: Vendor lock-in limits adoption
**Solution**: Use standard formats (markdown, YAML)
**Result**: Works with Claude Code, Gemini, Cursor, any AI tool

**Tool-Specific Features**: Only in `.claude/` directory
**Core Knowledge**: Always tool-agnostic in `.ai/`

---

## Information Flow Patterns

### Pattern 1: New Session Start

```
User opens project
    ↓
AI reads claude.md (orientation)
    ↓
AI reads INDEX.md (recent changes)
    ↓
AI checks GUIDE.md if needed (navigation help)
    ↓
AI ready to work with full context
```

**Time**: ~10 seconds
**Tokens**: ~5k tokens (vs. 50k+ for full-repo search)

### Pattern 2: Finding Feature Information

```
User asks: "How does authentication work?"
    ↓
AI reads INDEX.md (finds auth listed)
    ↓
AI reads knowledge/features/authentication.md
    ↓
AI answers with full context
```

**Time**: ~5 seconds
**Tokens**: ~2k tokens

### Pattern 3: Building New Feature

```
User requests new feature
    ↓
AI reads INDEX.md (context)
    ↓
AI reads related features (patterns)
    ↓
AI builds feature following patterns
    ↓
User runs /capture
    ↓
AI documents feature
    ↓
Knowledge base updated
```

**Result**: New feature + documentation generated

### Pattern 4: Cross-Tool Usage

```
Claude Code builds feature
    ↓
Runs /capture, documents it
    ↓
Later, user switches to Gemini
    ↓
Gemini reads claude.md → INDEX.md → feature docs
    ↓
Gemini has full context without searching
```

**Result**: Tool-agnostic knowledge transfer

---

## Scalability Considerations

### As Knowledge Grows

**Concern**: Will INDEX.md become too large?

**Solution**:
- Keep "Recent Changes" limited to last 10 entries
- Archive old changes to `.ai/archive/changes-YYYY-MM.md`
- INDEX.md always shows current state + recent changes

**Concern**: Will knowledge/ directories become unwieldy?

**Solution**:
- Features/components can be further categorized:
  - `knowledge/features/auth/` (auth-related features)
  - `knowledge/features/api/` (API features)
- Adjust based on project needs
- Start flat, reorganize when > 20 items

### As Projects Scale

**Multiple Repositories**:
- Each repo has its own `.ai/` directory
- Can link between repos in "related" frontmatter
- Shared patterns can be documented in a shared repo

**Team Collaboration**:
- Knowledge files merge like code
- Recent Changes may conflict (easy to resolve)
- Multiple people can run `/capture` on different features

---

## Extension Points

### Future Additions (Only If Needed)

**Workflows** (`.ai/workflows/`):
- If you repeat the same processes
- Standard operating procedures
- Checklists for common tasks

**Agents** (`.ai/agents/`):
- If you want specialized AI behaviors
- Code reviewer agent
- Test writer agent
- Documentation agent

**Skills** (`.ai/skills/`):
- Reusable templates
- Test generation templates
- Changelog update rules
- Migration patterns

**Archetypes** (`.ai/archetypes/`):
- Project structure templates
- REST API template
- CLI tool template
- Library template

**Philosophy**: Add these ONLY when you feel the need, not preemptively.

---

## Maintenance Strategy

### Automated (via `/capture`)

- Knowledge file creation/updates
- INDEX.md updates
- Cross-references
- Statistics updates

### Manual (Periodic)

**Weekly**:
- Review Recent Changes for accuracy
- Ensure critical features are documented

**Monthly**:
- Review and consolidate similar patterns
- Archive old Recent Changes
- Validate links still work

**Quarterly**:
- Assess if directory structure needs reorganization
- Prune deprecated knowledge
- Update GUIDE.md with new question patterns

---

## Technology Stack

### Current

- **Format**: Markdown with YAML frontmatter
- **Storage**: Git-tracked files
- **Integration**: Claude Code slash commands
- **Tools**: Standard git, text editors

### Future (Optional)

- **Validation Scripts**: Ensure consistent format
- **Search Tools**: Full-text search across knowledge
- **Analytics**: Track knowledge coverage
- **Templates**: More structured generators

---

## Success Metrics

### Performance

- **Discovery Time**: < 30 seconds to find information
- **Token Usage**: 70% reduction in repo searches
- **Coverage**: 100% of features documented

### Quality

- AI answers questions without clarification
- Features follow established patterns
- New developers get up to speed quickly
- Knowledge stays current with codebase

---

## Related Documentation

- [Overview](./overview.md) - What this project does and why
- [INDEX.md](../INDEX.md) - Current state and recent changes
- [GUIDE.md](../GUIDE.md) - How to navigate
- [claude.md](../../claude.md) - AI entry point

---

## Conclusion

This architecture balances **simplicity** with **scalability**:

- Simple enough to start immediately
- Structured enough to scale as projects grow
- Flexible enough to adapt to different needs
- Tool-agnostic enough to work anywhere

**Core Philosophy**: Let the project guide its evolution. Start minimal, add complexity only when needed.

---

**Last Updated**: 2025-11-08 (Foundation)
