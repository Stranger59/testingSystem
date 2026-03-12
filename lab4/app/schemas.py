from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TopicCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: Optional[str] = None


class TopicUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    description: Optional[str] = None


class TopicResponse(ORMModel):
    id: int
    title: str
    description: Optional[str] = None


class PublicAnswerOption(ORMModel):
    id: int
    text: str


class TestQuestionView(ORMModel):
    question_id: int
    order_no: int
    points: int
    text: str
    question_type: str
    difficulty: int
    options: List[PublicAnswerOption]


class TestDetailResponse(ORMModel):
    id: int
    title: str
    topic_id: int
    is_adaptive: bool
    created_at: datetime
    questions: List[TestQuestionView]


class AttemptCreate(BaseModel):
    student_id: int
    test_id: int


class AttemptResponse(ORMModel):
    id: int
    student_id: int
    test_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    score: float


class AnswerSubmit(BaseModel):
    question_id: int
    selected_option_ids: List[int] = []
    text_answer: Optional[str] = None


class AnswerSubmitResponse(BaseModel):
    student_answer_id: int
    question_id: int
    is_correct: bool
    awarded_points: int


class AttemptAnswerView(BaseModel):
    question_id: int
    text_answer: Optional[str] = None
    selected_option_ids: List[int]
    is_correct: Optional[bool] = None
    awarded_points: int


class AttemptDetailResponse(ORMModel):
    id: int
    student_id: int
    test_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    score: float
    answers: List[AttemptAnswerView]


class FinishAttemptResponse(BaseModel):
    attempt_id: int
    score: float
    max_score: int
    percentage: float
    recommendation: str


class AdaptiveTestGenerate(BaseModel):
    student_id: int
    topic_id: int
    based_on_attempt_id: int
    created_by: int = 1
    question_count: int = Field(default=5, ge=1, le=20)


class AdaptiveTestResponse(BaseModel):
    test_id: int
    title: str
    selected_question_ids: List[int]


class RecommendationResponse(ORMModel):
    id: int
    student_id: int
    topic_id: int
    attempt_id: int
    text: str
    created_at: datetime
