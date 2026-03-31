# Multi-Agent Research Paper Drafting System

Simple full-stack academic drafting assistant with a FastAPI backend, React frontend, MongoDB persistence, and a multi-agent generation pipeline.

## Stack

- Backend: FastAPI, Motor, Pydantic
- Frontend: React, Vite, plain CSS
- Database: MongoDB
- AI providers: OpenAI, Gemini, or `mock` mode
- Citation verification: Crossref

## Project Structure

- `backend/` FastAPI API, agents, services, and MongoDB repository
- `frontend/` React single-page app with a minimal futuristic UI

## Run Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs on `http://localhost:8000`.

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`.

## Environment

Copy `.env.example` to `.env` in the project root and fill in any API keys you want to use. The backend now reads either `research_drafter/.env` or `research_drafter/backend/.env`, so both layouts work.

- `LLM_PROVIDER=mock` keeps the app runnable without external credentials.
- `OPENAI_API_KEY` enables OpenAI generation.
- `GEMINI_API_KEY` enables Gemini generation.
- `MONGO_URI` points to your local or hosted MongoDB instance.

## API Endpoints

- `POST /generate-full`
- `POST /generate-section`
- `POST /verify-citations`
- `POST /export-md`
- `POST /export-latex`
- `POST /upload-pdf`

## Notes

- If MongoDB is unavailable, draft generation still works and saving simply falls back without crashing.
- Citation verification uses Crossref lookups and flags uncertain matches.
- PDF upload extracts likely references from a bibliography section for quick reuse.
