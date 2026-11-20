# 📚 NoteWise

An AI study assistant. Paste your notes or upload a PDF and NoteWise uses the **Gemini API** to generate a summary, key points, flashcards and a multiple-choice quiz, all in the language you choose.

## Features

- Text or PDF input (up to 5 MB, 30k characters)
- Structured output: Gemini is constrained to a JSON schema (Pydantic), so the UI never has to parse free text
- Interactive flashcards and a self-checking quiz with explanations
- Output language selector (English, Indonesian, Spanish, French)
- FastAPI backend with auto-generated docs at `/docs`
- Dockerized, runs as a non-root user, with a healthcheck
- Unit tests with the Gemini call mocked (no API key needed)

## Tech stack

Python 3.12 · FastAPI · Google Gen AI SDK (`google-genai`) · Pydantic · pypdf · Docker

## Run with Docker

```bash
cp .env.example .env        # then put your key in GEMINI_API_KEY
docker compose up --build
```

Open http://localhost:8000. Get a free API key at https://aistudio.google.com/apikey.

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
export GEMINI_API_KEY=your-key-here
uvicorn app.main:app --reload
```

## Tests

```bash
pytest
```

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/study-pack` | JSON body `{text, language, num_flashcards, num_questions}` |
| POST | `/api/study-pack/pdf` | multipart form: `file`, `language`, `num_flashcards`, `num_questions` |
| GET | `/health` | Liveness check |

Example:

```bash
curl -X POST http://localhost:8000/api/study-pack \
  -H "Content-Type: application/json" \
  -d '{"text": "Paste at least fifty characters of notes here, for example about photosynthesis...", "language": "English"}'
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | required | Google AI Studio key |
| `GEMINI_MODEL` | `gemini-3.5-flash` | Any Gemini model that supports JSON output |

## Project structure

```
app/
  main.py            # routes, PDF handling
  gemini_client.py   # prompt + structured Gemini call
  schemas.py         # Pydantic models (request + response schema)
  static/index.html  # single-page UI
tests/test_api.py
Dockerfile
docker-compose.yml
```

## Ideas for next steps

- Streaming responses
- Save study packs per user
- Export flashcards to Anki
