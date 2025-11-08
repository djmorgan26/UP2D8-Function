# /capture - Knowledge Capture Command

You are running the `/capture` command to systematically document recent work.

**Purpose**: Analyze git changes and automatically generate/update knowledge documentation.

**When to use**: After completing a feature, component, bug fix, or any significant work.

---

## Execution Steps

### Step 1: Analyze Changes

**Run these commands in parallel:**
- `git diff HEAD` - See uncommitted changes (if any)
- `git log -1 --stat` - See last commit details
- `git log -3 --oneline` - See recent commit context

**Extract**:
- Files modified/created/deleted
- Commit message(s) explaining what and why
- Lines changed (to estimate scope)

**Determine**:
- Is this a new feature?
- Is this a new component?
- Is this a bug fix?
- Is this a refactoring?
- Is this a new pattern?

### Step 2: Understand What Was Built

**Read the changed files:**
- Prioritize new files (likely new features/components)
- Check modified files to understand changes
- Look for key functions/classes/interfaces

**Identify**:
- **What** was built (feature name, component name)
- **Why** it was built (from commit messages, code comments)
- **How** it works (architecture, key functions)
- **Patterns used** (error handling, testing, structure)
- **Dependencies** (new packages, existing components used)
- **Key decisions** (why this approach vs alternatives)

### Step 3: Determine Knowledge Type

Based on your analysis, determine what type of knowledge to capture:

**Feature** - New user-facing functionality or system capability
- Examples: user authentication, password reset, email notifications
- Create: `.ai/knowledge/features/[feature-name].md`

**Component** - System module, service, or architectural piece
- Examples: API gateway, database layer, auth middleware
- Create: `.ai/knowledge/components/[component-name].md`

**Pattern** - Reusable coding pattern or convention
- Examples: error handling approach, testing strategy, dependency injection
- Create: `.ai/knowledge/patterns/[pattern-name].md`

**Decision** - Significant architectural or technical decision
- Examples: choice of framework, database selection, auth strategy
- Create: `.ai/context/decisions/NNN-decision-title.md`

**Note**: You may create multiple types for one change (e.g., feature + pattern + decision)

### Step 4: Create/Update Knowledge Files

**Use this template structure:**

```markdown
---
type: feature | component | pattern | decision
name: Human-Readable Name
status: implemented | in-progress | planned | deprecated
created: YYYY-MM-DD
updated: YYYY-MM-DD
files:
  - path/to/file1.ext
  - path/to/file2.ext
related:
  - .ai/knowledge/path/to/related.md
tags: [tag1, tag2, tag3]
---

# [Name]

## What It Does
[2-3 sentence description of what this is and its purpose]

## How It Works
[Detailed explanation of the architecture/implementation]

**Key files:**
- `path/to/file.ext:line` - Description of what this file does
- `path/to/another.ext:line` - Description

## Important Decisions
- **Decision 1**: Rationale
- **Decision 2**: Rationale

## Usage Example
```[language]
// Example code showing how to use this
```

## Testing
- Test files: `path/to/tests`
- Coverage: [percentage if known]
- Key test cases: [list]

## Common Issues
[If any known issues or gotchas]

## Related Knowledge
- [Related Feature/Component](./path/to/related.md)

## Future Ideas
- [ ] Potential improvement 1
- [ ] Potential improvement 2
```

**Guidelines:**
- Use kebab-case for filenames: `feature-name.md`
- Include file paths with line numbers where relevant: `src/auth.ts:45`
- Link to related knowledge files in frontmatter and body
- Add descriptive tags for searchability
- Be concise but complete
- Focus on "why" not just "what"

### Step 5: Update INDEX.md

**Add to Recent Changes section:**

```markdown
### YYYY-MM-DD
- [emoji] **Action**: Brief description → [filename](./knowledge/path/to/file.md)
```

**Emoji guide:**
- ✅ **Added**: New feature/component
- 🔧 **Refactored**: Code improvement
- 🐛 **Fixed**: Bug fix
- 📝 **Updated**: Documentation or enhancement
- 🎉 **Initialized**: Project setup
- 📊 **Improved**: Performance or quality improvement
- 🧪 **Testing**: Test additions/improvements

**Update knowledge counts:**

Find this section in INDEX.md:
```markdown
**Knowledge Items**: X features • Y components • Z patterns
```

Increment the appropriate counter(s).

**Update Knowledge Map section:**

Add links to new knowledge files in the appropriate section:
- Features list
- Components list
- Patterns list
- Decisions list

### Step 6: Validate

**Check**:
- [ ] All file references in knowledge docs exist
- [ ] YAML frontmatter is valid
- [ ] Links between knowledge files work
- [ ] INDEX.md Recent Changes updated
- [ ] Knowledge counts are correct
- [ ] File naming follows conventions (kebab-case)
- [ ] Created files are in correct directories

**If validation fails**: Fix issues before completing

### Step 7: Report to User

**Provide a summary:**

```
✅ Knowledge Captured

**Created:**
- .ai/knowledge/features/feature-name.md (234 lines)
- .ai/knowledge/patterns/pattern-name.md (112 lines)

**Updated:**
- .ai/INDEX.md (Recent Changes + knowledge counts)

**Documented:**
- 5 key files
- 2 important decisions
- 1 new pattern

**Next steps:**
- Review the generated documentation for accuracy
- Run tests if not already done
- Commit changes with: git add . && git commit -m "Add [feature] with documentation"
```

---

## Special Cases

### No Changes Detected

If `git diff HEAD` and `git log` show no recent changes:

```
⚠️  No recent changes detected.

Either:
1. Commit your changes first, then run /capture
2. Specify what to capture: /capture --describe "what you built"
```

### Multiple Features in One Commit

If the commit contains multiple distinct features:

1. Create separate knowledge files for each
2. Link them in the "Related Knowledge" sections
3. Update INDEX.md with multiple entries

### Updating Existing Knowledge

If the change enhances an existing feature:

1. Read the existing knowledge file
2. Update relevant sections
3. Update the `updated:` date in frontmatter
4. Add to "Recent Changes" in INDEX.md as "Updated"

### Large Refactoring

If the change affects many files but doesn't add new features:

1. Document the refactoring as a pattern (if reusable)
2. Update affected feature/component docs with new file references
3. Add ADR if architectural changes were made
4. Mark old patterns as deprecated if replaced

---

## Examples

### Example 1: New Feature

**Git changes:**
- Created: `src/auth/login.ts`, `src/auth/jwt.ts`
- Modified: `src/routes/index.ts`
- Commit: "Add user authentication with JWT"

**Actions:**
1. Create `.ai/knowledge/features/user-authentication.md`
2. Update `.ai/INDEX.md`:
   - Add to Recent Changes: "✅ **Added**: User authentication feature"
   - Increment feature count
   - Add to Features list in Knowledge Map
3. Link to any related components (e.g., database-layer.md)

### Example 2: New Pattern

**Git changes:**
- Created: `src/utils/error-handler.ts`
- Modified: Multiple files to use new error handling
- Commit: "Standardize error handling across API"

**Actions:**
1. Create `.ai/knowledge/patterns/error-handling.md`
2. Update affected feature docs to reference new pattern
3. Update `.ai/INDEX.md`:
   - Add to Recent Changes: "📝 **Added**: Error handling pattern"
   - Increment pattern count
   - Add to Patterns list

### Example 3: Bug Fix with Learning

**Git changes:**
- Modified: `src/auth/login.ts`
- Commit: "Fix token expiration validation"

**Actions:**
1. Update `.ai/knowledge/features/user-authentication.md`:
   - Add to "Common Issues" section
   - Document the bug and fix
   - Update `updated:` date
2. Update `.ai/INDEX.md`:
   - Add to Recent Changes: "🐛 **Fixed**: Token expiration in authentication"

---

## Best Practices

### DO:
- ✅ Run `/capture` immediately after completing work
- ✅ Include "why" explanations, not just "what"
- ✅ Link related knowledge files
- ✅ Add code examples when helpful
- ✅ Document important decisions
- ✅ Be concise but complete

### DON'T:
- ❌ Capture trivial changes (typo fixes, minor refactorings)
- ❌ Copy entire code files into knowledge docs
- ❌ Create knowledge files for every small function
- ❌ Skip updating INDEX.md
- ❌ Forget to validate file references

---

## Troubleshooting

**Problem**: Can't determine what type of knowledge to capture

**Solution**: Default to "feature" if user-facing, "component" if internal, "pattern" if reusable approach

---

**Problem**: Too many files changed to document

**Solution**: Focus on the most important files (public APIs, main logic), mention others in passing

---

**Problem**: Change is too small to warrant documentation

**Solution**: Skip /capture for trivial changes. Use it for meaningful additions only.

---

**Problem**: Existing knowledge file is outdated

**Solution**: Update it with new information, mark `updated:` field, note changes in Recent Changes

---

## Output Format

Always end with a clear summary showing:
1. What knowledge files were created/updated
2. What was documented
3. Next steps for the user

Keep the summary concise but informative.

---

**Remember**: The goal is to make future AI sessions efficient by having well-organized, discoverable knowledge. Quality over quantity.
