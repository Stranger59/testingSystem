from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine, get_db
from . import schemas, services


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        services.seed_demo_data(db)
    yield


app = FastAPI(
    title='Adaptive Biology Testing API',
    description=(
        'REST API для адаптивной системы тестирования студентов-биологов. '
        'Swagger доступен по /docs.'
    ),
    version='1.0.0',
    contact={
        'name': 'Laboratory work #4',
    },
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/health', tags=['Service'])
def healthcheck():
    return {'status': 'ok'}


@app.get('/topics', response_model=list[schemas.TopicResponse], tags=['Topics'])
def get_topics(db: Session = Depends(get_db)):
    return services.list_topics(db)


@app.post('/topics', response_model=schemas.TopicResponse, status_code=status.HTTP_201_CREATED, tags=['Topics'])
def create_topic(payload: schemas.TopicCreate, db: Session = Depends(get_db)):
    return services.create_topic(db, payload)


@app.put('/topics/{topic_id}', response_model=schemas.TopicResponse, tags=['Topics'])
def update_topic(topic_id: int, payload: schemas.TopicUpdate, db: Session = Depends(get_db)):
    return services.update_topic(db, topic_id, payload)


@app.delete('/topics/{topic_id}', status_code=status.HTTP_204_NO_CONTENT, tags=['Topics'])
def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    services.delete_topic(db, topic_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get('/tests/{test_id}', response_model=schemas.TestDetailResponse, tags=['Tests'])
def get_test_detail(test_id: int, db: Session = Depends(get_db)):
    return services.get_test_detail(db, test_id)


@app.post('/tests/generate-adaptive', response_model=schemas.AdaptiveTestResponse, status_code=status.HTTP_201_CREATED, tags=['Tests'])
def generate_adaptive_test(payload: schemas.AdaptiveTestGenerate, db: Session = Depends(get_db)):
    return services.generate_adaptive_test(db, payload)


@app.post('/attempts', response_model=schemas.AttemptResponse, status_code=status.HTTP_201_CREATED, tags=['Attempts'])
def create_attempt(payload: schemas.AttemptCreate, db: Session = Depends(get_db)):
    return services.create_attempt(db, payload)


@app.get('/attempts/{attempt_id}', response_model=schemas.AttemptDetailResponse, tags=['Attempts'])
def get_attempt(attempt_id: int, db: Session = Depends(get_db)):
    return services.get_attempt(db, attempt_id)


@app.post('/attempts/{attempt_id}/answers', response_model=schemas.AnswerSubmitResponse, tags=['Attempts'])
def submit_answer(attempt_id: int, payload: schemas.AnswerSubmit, db: Session = Depends(get_db)):
    return services.submit_answer(db, attempt_id, payload)


@app.post('/attempts/{attempt_id}/finish', response_model=schemas.FinishAttemptResponse, tags=['Attempts'])
def finish_attempt(attempt_id: int, db: Session = Depends(get_db)):
    return services.finish_attempt(db, attempt_id)


@app.get('/recommendations/student/{student_id}', response_model=list[schemas.RecommendationResponse], tags=['Recommendations'])
def list_recommendations(student_id: int, db: Session = Depends(get_db)):
    return services.list_recommendations_for_student(db, student_id)
