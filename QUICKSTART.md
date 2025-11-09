# Quick Start Guide

## 0. One `.env` to rule them all
Place your keys in the root-level `.env`:
```
OPENAI_API_KEY=sk-proj-***
FIRECRAWL_KEY=fc-***
DEEP_RESEARCH_API_URL=http://localhost:3051
```
`start_api.py` reads this file and boots the Node worker without any per-package env files.

## 1. Install dependencies (one time)
```bash
cd deep-research && npm install && cd ..
cd chatbot-frontend && npm install && cd ..
uv sync
```

## 2. Run the services (three terminals)
1. **Deep Research worker**
   ```bash
   uv run python start_api.py
   ```
2. **Backend API**
   ```bash
   cd backend
   uv run uvicorn main:app --reload
   ```
3. **Chatbot frontend**
   ```bash
   cd chatbot-frontend
   npm run dev
   ```

## 3. Smoke test the Python helper
```bash
uv run python resource_finder.py
```
or import `list_eligible_resources` inside your chatbot runtime.

## Files to know
- `start_api.py` — launches deep-research with env injection.
- `resource_finder.py` — callable helper used by the chatbot backend.
- `.env` — single source of truth for secret config.
