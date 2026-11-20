import os

from google import genai
from google.genai import types

from .schemas import StudyPack

DEFAULT_MODEL = "gemini-2.5-flash"

PROMPT = """You are a study assistant. Read the notes below and produce a study pack.

Rules:
- Write everything in {language}.
- Base every item ONLY on the notes; do not invent facts.
- key_points: 3-6 short bullets.
- flashcards: exactly {num_flashcards}.
- quiz: exactly {num_questions} multiple-choice questions with 4 options each,
  one correct answer (correct_index is 0-3) and a one-sentence explanation.

NOTES:
\"\"\"
{text}
\"\"\"
"""


class GeminiError(RuntimeError):
    pass


def _client() -> genai.Client:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise GeminiError("GEMINI_API_KEY is not set")
    return genai.Client(api_key=key)


def generate_study_pack(
    text: str, language: str = "English", num_flashcards: int = 6, num_questions: int = 4
) -> StudyPack:
    prompt = PROMPT.format(
        language=language,
        num_flashcards=num_flashcards,
        num_questions=num_questions,
        text=text,
    )
    try:
        response = _client().models.generate_content(
            model=os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=StudyPack,
                temperature=0.3,
            ),
        )
    except GeminiError:
        raise
    except Exception as exc:  # network, quota, auth, ...
        raise GeminiError(f"Gemini request failed: {exc}") from exc

    pack = response.parsed
    if not isinstance(pack, StudyPack):
        raise GeminiError("Gemini returned an unexpected response format")
    return pack
