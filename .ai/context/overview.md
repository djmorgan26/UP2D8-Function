# Project Overview

**Project Name**: UP2D8-Function - Automated Tasks Service
**Created**: 2025-11-08
**Status**: Active Development
**Repository**: UP2D8-Function

---

## What This Is

An **Azure Functions-based serverless application** for the UP2D8 platform. This service provides automated backend tasks for article aggregation and personalized newsletter delivery. It uses timer-triggered functions and durable functions orchestration to handle scheduled workloads.

Think of it as the **automation engine** for UP2D8 - handling all scheduled, serverless tasks behind the scenes.

---

## The Problem It Solves

### Challenges Addressed

The UP2D8 platform needs automated backend tasks to:

1. **Content Aggregation**: Regularly fetch articles from multiple RSS feeds
2. **Data Persistence**: Store scraped content in Cosmos DB for user access
3. **Personalization**: Generate customized newsletters based on user preferences
4. **Reliability**: Ensure scheduled tasks run consistently without manual intervention
5. **Scalability**: Handle growing numbers of feeds and users efficiently

### Real-World Impact

- ⏱️ **Daily Automation**: Articles scraped at 08:00 UTC, newsletters at 09:00 UTC
- 🔄 **Consistent Delivery**: Serverless functions ensure reliability
- 🎯 **Personalization**: AI-powered content generation for each user
- 📊 **Scalability**: Azure Functions scale automatically with load
- 🔐 **Security**: Azure Key Vault integration for secrets management

---

## The Solution

### Azure Functions Architecture

A serverless system with:

1. **Timer-Triggered Functions**: Scheduled tasks for scraping and newsletters
2. **Durable Functions**: Orchestration for complex workflows (crawling)
3. **Queue-Based Processing**: Azure Storage Queues for work distribution
4. **Managed Identity**: Secure access to Key Vault without hardcoded secrets
5. **Cosmos DB Integration**: MongoDB API for article and user data storage

### Key Components

**Functions**:
- **DailyArticleScraper**: Timer-triggered RSS feed scraper (08:00 UTC)
- **NewsletterGenerator**: Timer-triggered newsletter generation (09:00 UTC)
- **CrawlerOrchestrator**: Durable orchestrator for web crawling workflows
- **CrawlerWorker**: Activity function that performs individual crawls
- **ManualTrigger**: HTTP-triggered manual orchestration

**Shared Logic**:
- **orchestration_logic.py**: Reusable orchestration patterns
- Structured logging with `structlog`
- Key Vault secret retrieval utilities

### Workflow Example

Daily Article Scraping:
```
Timer triggers (08:00 UTC) → Fetch RSS feeds → Parse articles →
Store in Cosmos DB → Log results
```

Newsletter Generation:
```
Timer triggers (09:00 UTC) → Fetch user preferences →
Generate personalized content (AI) → Send newsletters → Update status
```

---

## How It Works

### The Flow

```
┌─────────────┐
│ New Session │
└──────┬──────┘
       │
       ├─> Read claude.md (orientation)
       │
       ├─> Read .ai/INDEX.md (what's new?)
       │
       ├─> Read .ai/GUIDE.md (where to look?)
       │
       ├─> Find specific knowledge
       │
       ├─> Build feature/fix bug
       │
       ├─> Run /capture
       │
       └─> Knowledge base updated
```

### Knowledge Capture Process

1. **Build something** (feature, component, fix)
2. **Run `/capture`**
3. **AI analyzes** git diff and changed files
4. **AI generates** structured documentation
5. **INDEX.md updates** with recent changes
6. **Next session**: Knowledge is available

### Incremental Growth

- **Day 1**: Foundation with 0 documented features
- **Week 1**: 2-3 features documented, patterns emerging
- **Month 1**: 10+ features, comprehensive pattern library
- **Month 3**: Complete knowledge base, AI rarely searches codebase

---

## Core Design Principles

### 1. Discovery Over Search
AI knows where to look first, reducing time and token costs

### 2. Incremental Knowledge Capture
Every feature adds to the knowledge base automatically

### 3. Tool Agnostic
Works with Claude Code, Gemini, Cursor, or any AI assistant

### 4. Human Readable
All files are markdown + YAML, easy to read and edit

### 5. Structured Navigation
Hierarchical: claude.md → INDEX.md → GUIDE.md → specific knowledge → code

### 6. Low Overhead
Simple `/capture` command, no complex setup per task

### 7. Git-Friendly
Plain text files tracked in git, merges easily, diff-able

---

## Current Status

### Phase: Active Development

**What's Built**:
- ✅ DailyArticleScraper function (RSS feed scraping)
- ✅ NewsletterGenerator function (newsletter creation)
- ✅ CrawlerOrchestrator (durable orchestration)
- ✅ CrawlerWorker (individual crawl tasks)
- ✅ ManualTrigger (manual orchestration trigger)
- ✅ Shared orchestration logic
- ✅ Azure Key Vault integration
- ✅ Cosmos DB (MongoDB API) integration
- ✅ Structured logging with `structlog`

**What's Next**:
1. Document existing functions using `/capture`
2. Add error handling patterns to knowledge base
3. Document orchestration workflows
4. Capture testing strategies

### Metrics (Current)

- **Functions**: 5 Azure Functions
- **Shared Components**: orchestration_logic.py
- **Dependencies**: 17 packages
- **Patterns**: Timer triggers, durable orchestration, queue-based workflows
- **Total knowledge files**: Foundation (to be populated via `/capture`)

---

## Use Cases

### For This Project (Meta-System)

This project IS the knowledge management system itself. It's self-documenting - as we build features for the system, we use `/capture` to document them.

### For Future Projects

Once established, this system can be:

1. **Copied to new projects** as a template
2. **Customized** for specific tech stacks
3. **Extended** with project-specific patterns
4. **Shared** across teams for consistency

### For Different AI Tools

- **Claude Code**: Full integration with `/capture` command and slash commands
- **Gemini/Bard**: Read `claude.md`, follow same file structure
- **Cursor**: Point to knowledge files, same navigation
- **GitHub Copilot**: Can reference knowledge files in prompts
- **Human Developers**: All files human-readable, serves as documentation

---

## Success Criteria

### Quantitative

- **Discovery time**: < 30 seconds to find relevant information
- **Search reduction**: 70%+ reduction in full-repo searches
- **Knowledge coverage**: 100% of features documented
- **Index hit rate**: 60%+ of questions answered from INDEX.md

### Qualitative

- AI provides context-aware answers without clarifying questions
- New features automatically follow established patterns
- Code reviews reference project-specific standards
- Knowledge base grows organically with minimal effort
- New developers (human or AI) get up to speed in minutes

---

## Technology Stack

### Platform & Runtime

- **Platform**: Azure Functions (Python 3.9+)
- **Runtime**: Azure Functions Core Tools v4
- **Deployment**: Azure CLI, VS Code Azure Extension

### Core Dependencies

**Azure Services**:
- `azure-functions` - Functions runtime
- `azure-identity` - Managed identity authentication
- `azure-keyvault-secrets` - Key Vault integration
- `azure-storage-queue` - Queue-based orchestration

**Data & Storage**:
- `pymongo` - Cosmos DB (MongoDB API) access
- `feedparser` - RSS feed parsing

**AI & Content Processing**:
- `google-generativeai` - Google Gemini API
- `langchain` & `langchain-community` & `langchain-google-genai` - LLM orchestration

**Web Scraping**:
- `playwright` - Browser automation
- `beautifulsoup4` - HTML parsing
- `lxml` - XML parsing

**Utilities**:
- `structlog` - Structured logging
- `python-dotenv` - Environment configuration
- `markdown` - Markdown processing

**Testing**:
- `pytest` - Test framework

### Future Enhancements

As the project evolves:
- **Monitoring**: Application Insights integration
- **Caching**: Redis for performance optimization
- **Testing**: Comprehensive unit and integration tests
- **CI/CD**: GitHub Actions for automated deployment

---

## Related Documentation

- [Architecture](./architecture.md) - How the system is structured
- [Decisions](./decisions/) - Major architectural decisions (empty for now)
- [INDEX.md](../INDEX.md) - Current state and recent changes
- [GUIDE.md](../GUIDE.md) - How to navigate the knowledge base
- [claude.md](../../claude.md) - AI entry point and orientation

---

## Philosophy

> "The best documentation is the one that's always up to date."

By capturing knowledge automatically as features are built, we eliminate the doc/code drift problem. Documentation is generated from reality (git changes) not aspirational intentions.

> "AI should know where to look, not search everything."

Structured navigation beats unstructured search. Like a well-organized library vs. a pile of books.

> "Start simple, grow organically."

Begin with minimal structure. Add complexity only when needed. Let the project guide its evolution.

---

**Last Updated**: 2025-11-08 (Foundation)
