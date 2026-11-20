import io
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pypdf import PdfReader

from .gemini_client import GeminiError, generate_study_pack
from .schemas import StudyPack, TextRequest

STATIC_DIR = Path(__file__).parent / "static"
MAX_PDF_BYTES = 5 * 1024 * 1024
MAX_CHARS = 30000

app = FastAPI(title="NoteWise", description="AI study assistant powered by Gemini", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/study-pack", response_model=StudyPack)
def study_pack_from_text(req: TextRequest) -> StudyPack:
    try:
        return generate_study_pack(req.text, req.language, req.num_flashcards, req.num_questions)
    except GeminiError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/api/study-pack/pdf", response_model=StudyPack)
async def study_pack_from_pdf(
    file: UploadFile = File(...),
    language: str = Form("English"),
    num_flashcards: int = Form(6),
    num_questions: int = Form(4),
) -> StudyPack:
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a .pdf file")
    data = await file.read()
    if len(data) > MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="PDF is larger than 5 MB")
    try:
        reader = PdfReader(io.BytesIO(data))
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read this PDF")
    if len(text) < 50:
        raise HTTPException(status_code=422, detail="No readable text found in the PDF")
    try:
        return generate_study_pack(
            text[:MAX_CHARS],
            language,
            max(1, min(num_flashcards, 15)),
            max(1, min(num_questions, 10)),
        )
    except GeminiError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
