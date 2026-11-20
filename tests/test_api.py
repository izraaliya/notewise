import io

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app import main
from app.gemini_client import GeminiError
from app.schemas import Flashcard, QuizQuestion, StudyPack

client = TestClient(main.app)

NOTES = "Photosynthesis is the process plants use to convert light into chemical energy. " * 3


def fake_pack() -> StudyPack:
    return StudyPack(
        title="Photosynthesis",
        summary="Plants turn light into energy.",
        key_points=["Light", "Chlorophyll", "Glucose"],
        flashcards=[Flashcard(question="What is it?", answer="Light to energy")],
        quiz=[QuizQuestion(question="Q?", options=["a", "b", "c", "d"], correct_index=2, explanation="Because.")],
    )


@pytest.fixture
def mock_gemini(monkeypatch):
    calls = []

    def fake(text, language, nf, nq):
        calls.append((text, language, nf, nq))
        return fake_pack()

    monkeypatch.setattr(main, "generate_study_pack", fake)
    return calls


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200 and "NoteWise" in r.text


def test_text_ok(mock_gemini):
    r = client.post("/api/study-pack", json={"text": NOTES, "language": "Indonesian", "num_flashcards": 3})
    assert r.status_code == 200
    assert r.json()["title"] == "Photosynthesis"
    assert mock_gemini[0][1:] == ("Indonesian", 3, 4)


def test_text_too_short():
    assert client.post("/api/study-pack", json={"text": "short"}).status_code == 422


def test_gemini_failure_is_502(monkeypatch):
    def boom(*a, **k):
        raise GeminiError("GEMINI_API_KEY is not set")

    monkeypatch.setattr(main, "generate_study_pack", boom)
    r = client.post("/api/study-pack", json={"text": NOTES})
    assert r.status_code == 502 and "GEMINI_API_KEY" in r.json()["detail"]


def test_pdf_rejects_non_pdf():
    r = client.post("/api/study-pack/pdf", files={"file": ("a.txt", b"hello", "text/plain")})
    assert r.status_code == 400


def test_pdf_without_text_is_422():
    buf = io.BytesIO()
    w = PdfWriter()
    w.add_blank_page(width=200, height=200)
    w.write(buf)
    r = client.post("/api/study-pack/pdf", files={"file": ("blank.pdf", buf.getvalue(), "application/pdf")})
    assert r.status_code == 422
