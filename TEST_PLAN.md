# Test Plan

Project: Liwaza GovData Assistant  
Date: 2026-06-10

## 1. Goal

This plan verifies that the application works end to end:

```text
React Frontend -> FastAPI MCP Server -> data.gouv.ci API
```

It also verifies that:

- tool execution is real;
- French and English work;
- empty states are readable;
- backend and frontend build successfully;
- documentation and endpoints are accessible.

## 2. Prerequisites

Backend:

- Python 3.12
- backend dependencies installed

Frontend:

- Node.js
- npm dependencies installed

## 3. Start Backend

```bash
cd /Users/zakaria/Desktop/liwaza/apps/backend
.venv312/bin/uvicorn app.main:app --reload
```

Expected:

```text
Uvicorn running on http://127.0.0.1:8000
```

Open:

```text
http://127.0.0.1:8000/docs
```

## 4. Start Frontend

In another terminal:

```bash
cd /Users/zakaria/Desktop/liwaza/apps/frontend
npm run dev
```

Expected:

```text
Local: http://127.0.0.1:5173/
```

Open:

```text
http://127.0.0.1:5173/
```

## 5. Backend Health Tests

Run:

```bash
curl -s http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"ok"}
```

Run:

```bash
curl -s http://127.0.0.1:8000/mcp/tools
```

Expected:

- JSON response;
- 11 tools listed;
- includes `search_public_datasets`.

## 6. Real API Tool Test

Run:

```bash
curl -s -X POST http://127.0.0.1:8000/mcp/tools/search_public_datasets \
  -H "Content-Type: application/json" \
  -d '{"query":"education","limit":2,"language":"fr"}'
```

Expected:

- `status`: `success`;
- `tool`: `search_public_datasets`;
- `source`: `data.gouv.ci`;
- non-empty `results` when API has matching data.

## 7. Chat API French Test

Run:

```bash
curl -s -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Trouve les datasets liés à l’éducation"}'
```

Expected:

- `language`: `fr`;
- `intent`: `search`;
- answer starts with `J'ai trouvé`;
- trace includes `search_public_datasets`.

## 8. Chat API English Test

Run:

```bash
curl -s -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Search datasets about health"}'
```

Expected:

- `language`: `en`;
- `intent`: `search`;
- answer starts with `I found`;
- trace query uses `health`.

## 9. Frontend French Flow

In the browser:

1. Keep language mode on `Auto`.
2. Click `Trouve les datasets liés à l'éducation`.
3. Check the answer.

Expected:

- UI remains French;
- answer is French;
- `Exécution des outils` appears;
- `Datasets publics` appears;
- rows are shown as `lignes`;
- no raw JSON is shown for normal results.

## 10. Frontend English Flow

In the browser:

1. Click `Nouvelle conversation`.
2. Type:

```text
Search datasets about health
```

3. Send.

Expected:

- UI switches to English;
- answer is English;
- `Tool execution` appears;
- `Public datasets` appears;
- `Language` in inspector is `en`.

## 11. Empty State Test

In the browser, type a very unlikely query:

```text
Trouve les datasets sur xyznotarealpublictopic
```

Expected:

- no raw JSON block;
- clear empty state;
- French message explains that no dataset was found.

## 12. Compare Indicator Test

In the browser:

```text
Compare les investissements entre 2020 et 2023
```

Expected:

- comparison card appears;
- values for 2020, 2021, 2022, 2023 appear;
- tool trace shows `compare_indicator_by_year`.

## 13. Selected Dataset Follow-Up Test

1. Search education datasets.
2. Click follow-up:

```text
Résume le dataset sélectionné.
```

Expected:

- summary uses the selected dataset from the previous result;
- no backend error;
- no raw JSON block;
- `Synthèse du dataset` appears.

## 14. Error State Test

1. Stop the backend.
2. Keep frontend running.
3. Send a message.

Expected:

- no raw `Failed to fetch`;
- message says backend API is unreachable;
- error is localized according to UI language.

## 15. Automated Checks

Backend:

```bash
cd /Users/zakaria/Desktop/liwaza/apps/backend
.venv312/bin/pytest
.venv312/bin/ruff check app tests
```

Expected:

- all tests pass;
- lint passes.

Frontend:

```bash
cd /Users/zakaria/Desktop/liwaza/apps/frontend
npm run build
npm audit --audit-level=moderate
```

Expected:

- build passes;
- audit reports 0 vulnerabilities.

## 16. Docker Test

Run from repo root:

```bash
cd /Users/zakaria/Desktop/liwaza
docker compose up --build
```

Open:

- frontend: `http://127.0.0.1:8080`
- backend: `http://127.0.0.1:8000/docs`

Expected:

- frontend loads;
- backend docs load;
- chat calls backend successfully.

## 17. Deployment Test

After deploying:

1. Open frontend public URL.
2. Open backend `/docs`.
3. Open backend `/mcp/tools`.
4. Send a French query from frontend.
5. Send an English query from frontend.
6. Verify browser network traffic goes to backend, not directly to data.gouv.ci.

Expected:

- deployed frontend works;
- deployed backend works;
- MCP tools are visible;
- tool execution is real.

## 18. Final Submission Verification

Before submitting:

- [ ] GitHub repository is public.
- [ ] Frontend URL works.
- [ ] Backend API URL works.
- [ ] MCP endpoint URL works.
- [ ] README is complete.
- [ ] Architecture document exists.
- [ ] AI strategy document exists.
- [ ] AI usage disclosure exists.
- [ ] Benchmark document exists.
- [ ] Screenshots added if available.
- [ ] Walkthrough video recorded.
