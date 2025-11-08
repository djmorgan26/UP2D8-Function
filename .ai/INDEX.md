# AI Knowledge Base Index

**Last Updated**: 2025-11-08
**Project Phase**: Active Development
**Knowledge Items**: 5 functions • 1 shared component • 0 patterns (to be documented)

---

## 🆕 Recent Changes

### 2025-11-08
- 🎉 **Initialized** AI knowledge management system for UP2D8-Function
- 📁 **Created** foundation structure (claude.md, INDEX.md, GUIDE.md)
- 📝 **Customized** context documentation for Azure Functions project
- 🔧 **Added** `/capture` command for automatic knowledge capture
- 📋 **Ready** to document existing functions and shared components

---

## 📍 Quick Navigation

**New to this project?** → Read [GUIDE.md](./GUIDE.md) to learn where to find things

### Project Context
- [Overview](./context/overview.md) - What this project does and why
- [Architecture](./context/architecture.md) - How the system is structured
- [Decisions](./context/decisions/) - Architecture Decision Records (ADRs) - **1 recorded**

### 🎨 Personal Preferences (Cross-Project Standards)
*These apply to all your projects and are referenced, not modified.*

- [Coding Standards](./preferences/coding-standards.md) - Naming, organization, quality principles
- [Error Handling](./preferences/error-handling.md) - Error patterns, logging, retry strategies
- [Testing Strategy](./preferences/testing-strategy.md) - Test philosophy, coverage, patterns
- [Documentation Style](./preferences/documentation-style.md) - Docs philosophy, formats, examples

### Knowledge Base (Grows over time)
- [Features](./knowledge/features/) - **1 documented** - Feature implementations
- [Components](./knowledge/components/) - **0 documented** - System components
- [Patterns](./knowledge/patterns/) - **0 documented** - Coding patterns

---

## 📊 Project Stats

- **Total knowledge files**: 7 (overview, architecture, 4 preferences, 1 decision)
- **Azure Functions**: 5 (DailyArticleScraper, NewsletterGenerator, CrawlerOrchestrator, CrawlerWorker, ManualTrigger)
- **Shared Components**: 1 (orchestration_logic.py)
- **Features documented**: 0 (ready to document with `/capture`)
- **Patterns captured**: 0 (ready to capture)
- **Decisions recorded**: 1
- **Personal preferences**: 4 (coding, errors, testing, docs)
- **Dependencies**: 17 Python packages
- **Test coverage**: To be determined
- **Last commit**: function running without errors for first time

---

## 🎯 Current Focus

**Phase**: Documenting existing Azure Functions project

**Next Steps**:
1. Run `/capture` to document existing functions
2. Document shared orchestration logic
3. Capture error handling and logging patterns
4. Document durable functions orchestration workflow

**Active Work**: Building knowledge base for established Azure Functions codebase

---

## 🗺️ Knowledge Map

### Azure Functions (5 - to be documented)
- 📝 **DailyArticleScraper** - Timer-triggered RSS feed scraper (08:00 UTC)
- 📝 **NewsletterGenerator** - Timer-triggered newsletter generation (09:00 UTC)
- 📝 **CrawlerOrchestrator** - Durable orchestrator for web crawling
- 📝 **CrawlerWorker** - Activity function for individual crawls
- 📝 **ManualTrigger** - HTTP trigger for manual orchestration

### Shared Components (1 - to be documented)
- 📝 **orchestration_logic.py** - Reusable orchestration patterns

### Patterns (0)
*Patterns will be captured via `/capture` as you document the codebase:*
- Timer-triggered functions
- Durable functions orchestration
- Queue-based workflows
- Key Vault secret management
- Structured logging patterns

### Decisions (1)
- ✅ [001: Personal Preferences System](./context/decisions/001-personal-preferences-system.md) - Cross-project standards approach

---

## 💡 How to Use This Index

**Every session, start here:**

1. **Check Recent Changes** (above) - See what's new since your last session
2. **Review Current Focus** - Understand what we're working on
3. **Use Quick Navigation** - Jump to relevant knowledge
4. **Read GUIDE.md** if you need help finding something specific

**After building something:**

1. Run `/capture` to automatically update this index
2. New knowledge files will be created/updated
3. Recent Changes section will be updated
4. Knowledge counts will increment

**This file is your dashboard** - it tells you everything that's happened and where to find what you need.

---

## 🔍 Quick Search Guide

| I need to... | Look in... |
|--------------|------------|
| See what's new | Recent Changes section above |
| Understand the project | [context/overview.md](./context/overview.md) |
| Learn the architecture | [context/architecture.md](./context/architecture.md) |
| Find a feature | [knowledge/features/](./knowledge/features/) (empty for now) |
| Find a component | [knowledge/components/](./knowledge/components/) (empty for now) |
| Learn patterns | [knowledge/patterns/](./knowledge/patterns/) (empty for now) |
| Understand decisions | [context/decisions/](./context/decisions/) (empty for now) |
| Navigate efficiently | [GUIDE.md](./GUIDE.md) |

---

## 📈 System Growth

This knowledge base will grow as you document the existing codebase:

- **Week 1**: Foundation + 5 Azure Functions documented
- **Week 2**: Shared components and patterns captured
- **Month 1**: Complete knowledge base with orchestration workflows, error handling patterns
- **Ongoing**: Update as new functions and features are added

**The system captures institutional knowledge of your Azure Functions project.**

---

## ⚡ Pro Tips

- **Check this file first** every session to see what's new
- **Run `/capture` regularly** to keep knowledge current
- **Use GUIDE.md** when you don't know where to look
- **Follow existing patterns** once they're documented
- **Update Recent Changes** whenever significant work is done

---

*This index is automatically updated by the `/capture` command and maintained by AI assistants working on this project.*
