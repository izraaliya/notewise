from pydantic import BaseModel, Field


class Flashcard(BaseModel):
    question: str
    answer: str


class QuizQuestion(BaseModel):
    question: str
    options: list[str] = Field(min_length=4, max_length=4)
    correct_index: int = Field(ge=0, le=3)
    explanation: str


class StudyPack(BaseModel):
    title: str
    summary: str
    key_points: list[str]
    flashcards: list[Flashcard]
    quiz: list[QuizQuestion]


class TextRequest(BaseModel):
    text: str = Field(min_length=50, max_length=30000)
    language: str = "English"
    num_flashcards: int = Field(default=6, ge=1, le=15)
    num_questions: int = Field(default=4, ge=1, le=10)
