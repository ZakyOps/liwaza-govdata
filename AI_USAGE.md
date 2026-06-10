# AI Usage Disclosure

Project: Liwaza GovData Assistant  
Date: 2026-06-10

## 1. Purpose

This document discloses how AI tools were used during the assessment.

The goal is not to hide AI usage. The goal is to show ownership, verification, and engineering judgment.

## 2. AI Tools Used

AI tools used:

- ChatGPT / Codex-style coding assistant
- Web research for current model and documentation references

No paid LLM is required at runtime for the MVP.

The application itself currently uses:

- deterministic intent routing;
- `lingua-language-detector` for language detection;
- real MCP tool execution against data.gouv.ci.

## 3. Prompts Used

The working prompts were written in natural French during the build. Below are representative prompts rewritten in a clearer engineering format, while preserving the actual intent of the requests.

```text
Read the Junior Full Stack Engineer assessment, identify all required deliverables, and benchmark public API options that could fit an AI-native eGov MCP platform.
```

```text
Assume we choose https://data.gouv.ci/ as the government data source. Explain the product concept, the user value, the MCP architecture, and the concrete implementation path.
```

```text
Explain MCP in simple terms, then map it to this project: React as MCP client, FastAPI as MCP server, backend tools calling data.gouv.ci, and traceable tool execution.
```

```text
Expand the scope to at least 15 backend endpoints and at least 10 MCP tools. Then implement the monorepo with FastAPI, Pydantic, React, TypeScript, Docker, CI, and documentation.
```

```text
Review the interface and code structure for readability. Make the product feel professional, clear, and suitable for an engineering assessment rather than a generic AI demo.
```

```text
Debug the French-language mode. Ensure that frontend labels, backend answers, follow-up questions, and tool traces stay consistent when the user writes in French.
```

```text
Implement automatic user-language detection so the assistant responds in French or English without requiring the user to manually select a mode.
```

```text
Improve language detection without relying only on predefined keyword lists. Use a real language-detection library and keep a small fallback for short ambiguous messages.
```

```text
Re-read the required deliverables and produce the missing documents: architecture decision document, AI/LLM strategy, AI usage disclosure, complete README, and a test plan.
```

```text
Audit the project against Clean Code principles from the Odoo 19.0 docs. Apply relevant improvements: intention-revealing names, smaller functions, single responsibility, clear tests, and minimal comments.
```

```text
The search results include datasets from data.gouv.fr. Fix the backend so the assistant keeps the data.gouv.ci/Côte d'Ivoire scope while keeping the user-facing wording natural.
```

```text
Improve the AI strategy prompt section. Write production-quality prompts like a prompt engineer would: system prompt, tool-routing prompt, parameter extraction, grounded answer, safety review, and evaluation prompts.
```

## 4. AI-Assisted Parts

AI assistance was used for:

- interpreting the technical assessment;
- benchmarking possible public APIs;
- proposing the product scope;
- drafting the cahier des charges;
- designing the MCP tool list;
- scaffolding the FastAPI backend;
- scaffolding the React frontend;
- writing documentation drafts;
- improving UI text and structure;
- identifying and fixing bugs;
- writing test strategy and commands.

## 5. Manually Verified Parts

The following were manually verified through commands and browser checks:

- PDF content extraction;
- data.gouv.ci API availability;
- Data Fair endpoint responses;
- FastAPI backend startup;
- MCP tool listing;
- real `search_public_datasets` API execution;
- React production build;
- backend tests;
- backend lint;
- npm audit;
- automatic FR/EN language detection;
- frontend empty-state and error behavior.

## 6. AI-Generated Outputs Reviewed

AI-generated code and text were reviewed for:

- correctness;
- alignment with the assessment;
- no fake tool execution;
- no hardcoded public-data results;
- clean architecture;
- ability to run locally;
- readable documentation;
- professional UI tone.

## 7. AI-Generated Outputs Changed Manually

Several AI-generated parts were corrected or improved:

- changed language detection from keyword heuristics to `lingua-language-detector`;
- improved frontend empty states;
- improved backend error clarity;
- changed result rendering from raw JSON to professional cards;
- added real selected-dataset context for follow-up actions;
- added more tests after bugs were found;
- improved French/English UI consistency.

## 8. Verification Responsibility

The candidate remains responsible for:

- code correctness;
- factual accuracy;
- security assumptions;
- deployment configuration;
- architecture decisions;
- final video explanation.

AI was used as an engineering assistant, not as an unchecked source of truth.

## 9. Known Limitations

Current MVP limitations:

- no persistent database;
- no user accounts;
- no production OAuth;
- no full load test;
- no deployed public URLs yet;
- no walkthrough video recorded yet;
- not all data.gouv.ci datasets have equally clean metadata.

## 10. Runtime AI Disclosure

The current application does not require an LLM provider at runtime.

The "AI-native" behavior comes from:

- natural language interface;
- language detection;
- intent routing;
- MCP tool orchestration;
- structured and traceable public-data responses.

Future LLM integration is documented in `AI_STRATEGY.md`.
