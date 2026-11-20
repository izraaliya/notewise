# 📚 NoteWise

**An AI study assistant.** Paste your notes or upload a PDF, and NoteWise uses the **Gemini API** to generate a summary, key points, flashcards and a multiple-choice quiz, in the language you choose.

## Features

- **Text or PDF input** (PDF up to 5 MB; text is capped at 30,000 characters)
- **Structured output:** Gemini is constrained to a JSON schema (Pydantic), so the UI never has to parse free text
- **Interactive study tools:** click-to-reveal flashcards and a self-checking quiz with explanations
- **Multilingual output:** English, Indonesian, Spanish, French
- **FastAPI backend** with auto-generated API docs at `/docs`
- **Docker support:** non-root container with a healthcheck
- **Tests** with the Gemini call mocked, so no API key is needed to run them

## Tech stack

Python 3.12 · FastAPI · Google Gen AI SDK (`google-genai`) · Pydantic · pypdf · Vanilla JS · Docker

## How it works

```
Browser ──(text / PDF)──► FastAPI ──(prompt + JSON schema)──► Gemini
   ▲                         │                                    │
   └────── StudyPack JSON ◄──┴──── validated with Pydantic ◄──────┘
```

1. The browser sends text, or a PDF that the server extracts text from with `pypdf`.
2. The server builds a prompt that tells Gemini to use only the provided notes.
3. Gemini replies in JSON that matches the `StudyPack` schema (title, summary, key points, flashcards, quiz).
4. The response is validated and rendered as interactive cards and a quiz.

## Getting started

You need a free Gemini API key from https://aistudio.google.com/apikey.

### Option A: Python (no Docker needed)

```bash
git clone https://github.com/izraaliya/notewise.git
cd notewise

python -m venv .venv
source .venv/bin/activate          # Git Bash on Windows: source .venv/Scripts/activate
                                   # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

export GEMINI_API_KEY=your-key-here    # PowerShell: $env:GEMINI_API_KEY="your-key-here"
uvicorn app.main:app --reload
```

Open http://localhost:8000.

### Option B: Docker

```bash
cp .env.example .env               # then put your key in GEMINI_API_KEY
docker compose up --build
```

Open http://localhost:8000.

> The Python option reads the key from the environment variable only. The Docker option reads it from `.env`. Never commit `.env`; it is already in `.gitignore`.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | required | Google AI Studio API key |
| `GEMINI_MODEL` | `gemini-3.5-flash` | Any Gemini model that supports JSON output |

## API

Interactive docs are available at http://localhost:8000/docs.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/study-pack` | JSON body: `text`, `language`, `num_flashcards`, `num_questions` |
| `POST` | `/api/study-pack/pdf` | Multipart form: `file`, `language`, `num_flashcards`, `num_questions` |
| `GET` | `/health` | Liveness check |

Example:

```bash
curl -X POST http://localhost:8000/api/study-pack \
  -H "Content-Type: application/json" \
  -d '{"text": "Photosynthesis is how plants convert light into chemical energy stored as glucose.", "language": "English"}'
```

The text must be at least 50 characters, so lengthen the example if you get a `422`.

## Tests

```bash
pytest
```

The tests mock the Gemini client, so they run offline and need no API key.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `GEMINI_API_KEY is not set` | Export the key in the same terminal that runs `uvicorn` (it does not persist across terminals) |
| `404 NOT_FOUND ... model ... no longer available` | Set `GEMINI_MODEL` to a current model, e.g. `gemini-3.5-flash` |
| `503 UNAVAILABLE ... high demand` | The model is busy; retry, or try `GEMINI_MODEL=gemini-3.5-flash-lite` |
| "No readable text found in the PDF" | The PDF is probably a scan (images only); NoteWise does not do OCR |
| `docker: command not found` | Install Docker Desktop, or use Option A |

## Project structure

```
app/
  main.py             # routes, PDF text extraction
  gemini_client.py    # prompt + structured Gemini call
  schemas.py          # Pydantic models (request + response schema)
  static/index.html   # single-page UI
tests/
  test_api.py
Dockerfile
docker-compose.yml
requirements.txt
requirements-dev.txt
```

## Limitations

- Scanned PDFs are not supported (no OCR).
- Very long documents are truncated to the first 30,000 characters.
- Quiz and flashcard quality depends on the model; always review the output.

## Roadmap

- Streaming responses
- Saving study packs per user
- Export flashcards to Anki
- OCR for scanned PDFs
