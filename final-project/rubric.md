# 🎓 Final Project — AI-Powered Application

## Overview

Build and ship a **production-quality application** that leverages AI/LLM capabilities. This is your chance to apply everything from the course — prompting, tool calling, autonomous agents, MCP, TDD, multi-stack awareness — into a single cohesive project.

**Theme:** Free choice. Build something you actually want to use.

**Deadline:** Week 8 study session (Demo Day)

**Submission:** PR to `submissions/{initials}/final-project/` with title `[Final - {initials}]`

---

## Requirements

### Must-Haves
1. **Working application** — It runs. A reviewer can clone, install, and use it locally with clear instructions.
2. **AI/LLM integration** — The app must use at least one LLM in a meaningful way (not just a chat wrapper).
3. **Persistence** — Some form of data storage (DB, file, vector store, etc.).
4. **README** — Setup instructions, architecture overview, design decisions.
5. **Demo** — 5-minute live demo + 2-minute Q&A during Demo Day.

### Nice-to-Haves (bonus points)
- Deployed/accessible URL
- Multiple AI techniques (RAG, agents, tool calling, multi-model)
- Claude Code automations used during development (`.claude/commands/`, `CLAUDE.md`, SubAgents)
- Test coverage
- CI/CD pipeline

---

## Scoring Rubric (100 points)

### 1. Technical Depth (30 pts)

| Score | Criteria |
|-------|----------|
| 25-30 | Sophisticated AI integration: multi-step agents, RAG pipeline, tool calling, or novel LLM application. Clear architectural reasoning. |
| 18-24 | Solid AI integration with at least 2 distinct techniques. Good separation of concerns. |
| 10-17 | Basic LLM API call with some prompt engineering. Functional but straightforward. |
| 0-9 | Minimal AI usage (simple chat completion wrapper with no added value). |

**What counts:**
- Prompt engineering quality (structured prompts, few-shot, CoT)
- Agent design (tool definitions, error handling, fallback logic)
- RAG implementation (chunking strategy, retrieval quality, re-ranking)
- Multi-model orchestration
- MCP server/client usage

### 2. Product Quality (25 pts)

| Score | Criteria |
|-------|----------|
| 21-25 | Polished, intuitive UX. Handles edge cases gracefully. Feels like a real product someone would use. |
| 15-20 | Clean UI, core flows work well. Minor rough edges but clearly usable. |
| 8-14 | Functional but bare-bones. Works for the demo but limited real-world usability. |
| 0-7 | Broken flows, confusing UX, or incomplete core features. |

**What counts:**
- User experience (flow, feedback, error states)
- Feature completeness (core use case fully works end-to-end)
- Visual design (doesn't need to be beautiful, but should be intentional)
- Edge case handling

### 3. Code Quality & Engineering (20 pts)

| Score | Criteria |
|-------|----------|
| 17-20 | Clean architecture, meaningful tests, proper error handling, good abstractions. Evidence of AI-assisted development workflow (CLAUDE.md, commands, SubAgents). |
| 12-16 | Organized code, some tests, reasonable structure. |
| 6-11 | Code works but messy. No tests. Poor separation of concerns. |
| 0-5 | Spaghetti code, no structure, copy-paste without understanding. |

**What counts:**
- Project structure and organization
- Test coverage (unit, integration, or e2e — any counts)
- Error handling and logging
- Use of Claude Code features during development (show your `.claude/` setup)
- Git history quality (meaningful commits, not one giant commit)

### 4. Demo & Communication (15 pts)

| Score | Criteria |
|-------|----------|
| 13-15 | Compelling narrative. Clear problem → solution → demo flow. Handles Q&A confidently. Shows genuine enthusiasm. |
| 9-12 | Solid demo covering all features. Explains decisions. Adequate Q&A. |
| 5-8 | Demo works but lacks structure or clarity. Struggles with Q&A. |
| 0-4 | Unprepared, app crashes during demo, or unable to explain decisions. |

**What counts:**
- Problem framing (why does this matter?)
- Live demo execution (smooth, rehearsed)
- Architecture walkthrough (brief but clear)
- Q&A responses (depth of understanding)

### 5. Ambition & Originality (10 pts)

| Score | Criteria |
|-------|----------|
| 9-10 | Novel idea or creative application of AI. Goes significantly beyond course examples. |
| 6-8 | Interesting twist on a known concept. Some original thinking. |
| 3-5 | Standard project idea (todo app + AI, chatbot, summarizer) but well-executed. |
| 0-2 | Minimal effort, rehash of weekly assignments. |

---

## Project Ideas (for inspiration)

These are suggestions — feel free to go in any direction.

| Category | Example |
|----------|---------|
| **Developer Tools** | AI code reviewer, automated PR summarizer, intelligent commit message generator |
| **Productivity** | Meeting notes → action items pipeline, AI-powered bookmark manager, smart email drafter |
| **Data & Research** | Paper summarizer with RAG, dataset explorer with natural language queries, competitive analysis agent |
| **Creative** | AI dungeon master, collaborative story writer, music playlist curator with explanations |
| **Business** | Customer support agent with tool calling, invoice data extractor, smart CRM assistant |
| **Education** | Adaptive quiz generator, concept explainer with visual aids, language practice partner |

---

## Timeline

| When | What |
|------|------|
| **Now** | Start brainstorming. Pick your idea. |
| **Week 7 study** | (Optional) Brief pitch: 1-minute idea share for early feedback. |
| **Week 8 study (Demo Day)** | Final submission PR + 5-min demo + 2-min Q&A. |

---

## Submission Checklist

- [ ] PR submitted to `submissions/{initials}/final-project/`
- [ ] README.md with setup instructions and architecture overview
- [ ] Application runs locally with documented steps
- [ ] `.env.example` with required environment variables
- [ ] Demo prepared (5 minutes)

---

*"The best way to predict the future is to build it." — Alan Kay*
