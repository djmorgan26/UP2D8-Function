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
- ✅ **Documented** all 5 Azure Functions with comprehensive details
- ✅ **Documented** shared orchestration logic component
- 📊 **Captured** patterns: timer triggers, queue-based processing, AI integration
- 🎯 **Status**: Complete knowledge base for existing codebase

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

- **Total knowledge files**: 13 (overview, architecture, 5 functions, 1 component, 4 preferences, 1 decision)
- **Azure Functions**: 5 (DailyArticleScraper, NewsletterGenerator, CrawlerOrchestrator, CrawlerWorker, ManualTrigger)
- **Shared Components**: 1 (orchestration_logic.py)
- **Features documented**: 5 ✅ (all functions documented)
- **Components documented**: 1 ✅ (orchestration logic)
- **Patterns captured**: 3 (timer triggers, queue-based, AI integration)
- **Decisions recorded**: 1
- **Personal preferences**: 4 (coding, errors, testing, docs)
- **Dependencies**: 17 Python packages
- **Test coverage**: To be determined
- **Last commit**: Add AI knowledge management system

---

## 🎯 Current Focus

**Phase**: Knowledge base complete - Ready for development

**Completed**:
1. ✅ Documented all 5 Azure Functions
2. ✅ Documented shared orchestration logic
3. ✅ Captured key patterns (timers, queues, AI integration)
4. ✅ Established comprehensive knowledge base

**Next Steps**:
1. Use knowledge base for feature development
2. Update docs as new features are added
3. Capture new patterns as they emerge
4. Leverage `/capture` for future changes

**Active Work**: Knowledge base ready to support development

---

## 🗺️ Knowledge Map

### Azure Functions (5 ✅ Fully Documented)

**Article Discovery & Processing**:
- ✅ **[DailyArticleScraper](./knowledge/features/daily-article-scraper.md)** - Timer-triggered RSS feed scraper (08:00 UTC)
  - Fetches articles from RSS feeds stored in Cosmos DB
  - Auto-assigns tags using keyword-based classification
  - Prevents duplicates with unique index on link field
  - Daily execution to ensure fresh content

- ✅ **[NewsletterGenerator](./knowledge/features/newsletter-generator.md)** - Timer-triggered newsletter generation (09:00 UTC)
  - AI-powered personalized newsletter creation using Google Gemini
  - Filters articles by user-subscribed tags
  - Converts Markdown to HTML for email delivery
  - Sends via Brevo SMTP service

**Intelligent Web Crawling**:
- ✅ **[CrawlerOrchestrator](./knowledge/features/crawler-orchestrator.md)** - Timer-triggered orchestrator (11:00 UTC)
  - Discovers articles via Google Custom Search API
  - Uses shared orchestration logic
  - Outputs URLs to queue via function binding
  - Implements fan-out pattern

- ✅ **[CrawlerWorker](./knowledge/features/crawler-worker.md)** - Queue-triggered web scraper
  - Headless browser automation with Playwright
  - Intelligent content extraction using BeautifulSoup
  - Processes one URL per instance (parallel execution)
  - Stores full article content in Cosmos DB

**Manual Operations**:
- ✅ **[ManualTrigger](./knowledge/features/manual-trigger.md)** - HTTP-triggered manual orchestration
  - On-demand article discovery
  - Uses same core logic as CrawlerOrchestrator
  - Explicitly manages queue operations
  - Enables testing and ad-hoc runs

### Shared Components (1 ✅ Fully Documented)

- ✅ **[orchestration_logic.py](./knowledge/components/orchestration-logic.md)** - Reusable article discovery logic
  - Aggregates user topics from Cosmos DB
  - Searches Google for latest articles
  - Deduplicates against existing articles
  - Shared by CrawlerOrchestrator and ManualTrigger

### Patterns (3 Captured)

**Captured Patterns**:
- ✅ **Timer-Triggered Functions** - Scheduled execution (CRON expressions)
- ✅ **Queue-Based Processing** - Fan-out pattern for parallel work distribution
- ✅ **AI Integration** - Google Gemini for newsletter content generation

**Additional Patterns Found**:
- Structured logging with `structlog`
- Azure Key Vault secrets management
- Duplicate prevention via unique indexes
- Error isolation (per-item error handling)
- Shared module reusability
- Async function execution (CrawlerWorker)
- Headless browser automation (Playwright)

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

Knowledge base **complete** for existing codebase:

- ✅ **Day 1**: Foundation + AI knowledge system integrated
- ✅ **Day 1**: All 5 Azure Functions fully documented
- ✅ **Day 1**: Shared orchestration logic captured
- ✅ **Day 1**: Key patterns identified and documented
- **Ongoing**: Update via `/capture` as new functions/features are added

**The system now contains complete institutional knowledge of your Azure Functions project.**

---

## ⚡ Pro Tips

- **Check this file first** every session to see what's new
- **Run `/capture` regularly** to keep knowledge current
- **Use GUIDE.md** when you don't know where to look
- **Follow existing patterns** once they're documented
- **Update Recent Changes** whenever significant work is done

---

*This index is automatically updated by the `/capture` command and maintained by AI assistants working on this project.*
