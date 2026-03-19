from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Set

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from . import models, schemas


def seed_demo_data(db: Session) -> None:
    if db.scalar(select(models.Role.id).limit(1)):
        return

    teacher_role = models.Role(name='TEACHER')
    student_role = models.Role(name='STUDENT')
    admin_role = models.Role(name='ADMIN')
    db.add_all([teacher_role, student_role, admin_role])
    db.flush()

    teacher = models.User(
        full_name='Dr. Elena Smirnova',
        email='teacher@bio.local',
        password_hash='demo_hash_teacher',
        role_id=teacher_role.id,
    )
    student = models.User(
        full_name='Ivan Petrov',
        email='student@bio.local',
        password_hash='demo_hash_student',
        role_id=student_role.id,
    )
    db.add_all([teacher, student])
    db.flush()

    topic_1 = models.Topic(
        title='Клеточная биология',
        description='Строение клетки, органоиды и их функции.',
    )
    topic_2 = models.Topic(
        title='Генетика',
        description='Основы наследственности и изменчивости.',
    )
    topic_3 = models.Topic(
        title='Ботаника',
        description='Демонстрационная свободная тема для удаления.',
    )
    db.add_all([topic_1, topic_2, topic_3])
    db.flush()

    q1 = models.Question(
        topic_id=topic_1.id,
        text='Какая органелла отвечает за синтез АТФ?',
        question_type='single_choice',
        difficulty=1,
    )
    q2 = models.Question(
        topic_id=topic_1.id,
        text='Выберите структуры, характерные для эукариотической клетки.',
        question_type='multiple_choice',
        difficulty=2,
    )
    q3 = models.Question(
        topic_id=topic_1.id,
        text='Как называется полужидкая внутренняя среда клетки?',
        question_type='text',
        difficulty=1,
    )
    q4 = models.Question(
        topic_id=topic_1.id,
        text='Какой органоид содержит гидролитические ферменты?',
        question_type='single_choice',
        difficulty=3,
    )
    q5 = models.Question(
        topic_id=topic_1.id,
        text='Какая структура отделяет клетку от внешней среды?',
        question_type='single_choice',
        difficulty=1,
    )
    q6 = models.Question(
        topic_id=topic_1.id,
        text='Как называется двумембранный органоид, в котором содержится ДНК и происходит клеточное дыхание?',
        question_type='text',
        difficulty=2,
    )
    db.add_all([q1, q2, q3, q4, q5, q6])
    db.flush()

    db.add_all([
        models.AnswerOption(question_id=q1.id, text='Митохондрия', is_correct=True),
        models.AnswerOption(question_id=q1.id, text='Рибосома', is_correct=False),
        models.AnswerOption(question_id=q1.id, text='Аппарат Гольджи', is_correct=False),

        models.AnswerOption(question_id=q2.id, text='Ядро', is_correct=True),
        models.AnswerOption(question_id=q2.id, text='Митохондрия', is_correct=True),
        models.AnswerOption(question_id=q2.id, text='Нуклеоид', is_correct=False),
        models.AnswerOption(question_id=q2.id, text='Лизосома', is_correct=True),

        models.AnswerOption(question_id=q3.id, text='Цитоплазма', is_correct=True),
        models.AnswerOption(question_id=q3.id, text='Цитозоль', is_correct=True),

        models.AnswerOption(question_id=q4.id, text='Лизосома', is_correct=True),
        models.AnswerOption(question_id=q4.id, text='Центросома', is_correct=False),
        models.AnswerOption(question_id=q4.id, text='Рибосома', is_correct=False),

        models.AnswerOption(question_id=q5.id, text='Клеточная мембрана', is_correct=True),
        models.AnswerOption(question_id=q5.id, text='Ядрышко', is_correct=False),
        models.AnswerOption(question_id=q5.id, text='Хлоропласт', is_correct=False),

        models.AnswerOption(question_id=q6.id, text='Митохондрия', is_correct=True),
    ])
    db.flush()

    base_test = models.Test(
        title='Базовый тест: клеточная биология',
        topic_id=topic_1.id,
        created_by=teacher.id,
        is_adaptive=False,
    )
    db.add(base_test)
    db.flush()

    for order_no, question in enumerate([q1, q2, q3], start=1):
        db.add(models.TestQuestion(test_id=base_test.id, question_id=question.id, order_no=order_no, points=2))

    db.commit()


def list_topics(db: Session):
    return db.scalars(select(models.Topic).order_by(models.Topic.id)).all()


def create_topic(db: Session, payload: schemas.TopicCreate):
    topic = models.Topic(title=payload.title, description=payload.description)
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


def update_topic(db: Session, topic_id: int, payload: schemas.TopicUpdate):
    topic = db.get(models.Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Topic not found')

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(topic, field, value)

    db.commit()
    db.refresh(topic)
    return topic


def delete_topic(db: Session, topic_id: int):
    topic = db.get(models.Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Topic not found')

    has_questions = db.scalar(select(models.Question.id).where(models.Question.topic_id == topic_id).limit(1))
    has_tests = db.scalar(select(models.Test.id).where(models.Test.topic_id == topic_id).limit(1))
    if has_questions or has_tests:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Topic cannot be deleted because it is referenced by questions or tests',
        )

    db.delete(topic)
    db.commit()


def get_test_detail(db: Session, test_id: int):
    test = db.scalar(
        select(models.Test)
        .options(
            joinedload(models.Test.test_questions)
            .joinedload(models.TestQuestion.question)
            .joinedload(models.Question.answer_options)
        )
        .where(models.Test.id == test_id)
    )
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Test not found')

    questions = []
    for item in sorted(test.test_questions, key=lambda x: x.order_no):
        questions.append(
            schemas.TestQuestionView(
                question_id=item.question.id,
                order_no=item.order_no,
                points=item.points,
                text=item.question.text,
                question_type=item.question.question_type,
                difficulty=item.question.difficulty,
                options=[schemas.PublicAnswerOption.model_validate(opt) for opt in item.question.answer_options],
            )
        )

    return schemas.TestDetailResponse(
        id=test.id,
        title=test.title,
        topic_id=test.topic_id,
        is_adaptive=test.is_adaptive,
        created_at=test.created_at,
        questions=questions,
    )


def create_attempt(db: Session, payload: schemas.AttemptCreate):
    student = db.get(models.User, payload.student_id)
    test = db.get(models.Test, payload.test_id)
    if not student or not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Student or test not found')

    attempt = models.Attempt(student_id=payload.student_id, test_id=payload.test_id, score=0)
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def get_attempt(db: Session, attempt_id: int):
    attempt = db.scalar(
        select(models.Attempt)
        .options(
            joinedload(models.Attempt.student_answers).joinedload(models.StudentAnswer.selected_options)
        )
        .where(models.Attempt.id == attempt_id)
    )
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Attempt not found')

    answers = []
    for answer in attempt.student_answers:
        answers.append(
            schemas.AttemptAnswerView(
                question_id=answer.question_id,
                text_answer=answer.text_answer,
                selected_option_ids=[item.answer_option_id for item in answer.selected_options],
                is_correct=answer.is_correct,
                awarded_points=answer.awarded_points or 0,
            )
        )

    return schemas.AttemptDetailResponse(
        id=attempt.id,
        student_id=attempt.student_id,
        test_id=attempt.test_id,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        score=float(attempt.score or 0),
        answers=answers,
    )


def _get_correct_option_ids(question: models.Question) -> Set[int]:
    return {option.id for option in question.answer_options if option.is_correct}


def _get_question_points(test: models.Test, question_id: int) -> int:
    for item in test.test_questions:
        if item.question_id == question_id:
            return item.points
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Question is not part of the selected test')


def submit_answer(db: Session, attempt_id: int, payload: schemas.AnswerSubmit):
    attempt = db.scalar(
        select(models.Attempt)
        .options(
            joinedload(models.Attempt.test)
            .joinedload(models.Test.test_questions)
            .joinedload(models.TestQuestion.question)
            .joinedload(models.Question.answer_options),
            joinedload(models.Attempt.student_answers).joinedload(models.StudentAnswer.selected_options),
        )
        .where(models.Attempt.id == attempt_id)
    )
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Attempt not found')
    if attempt.completed_at:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Attempt is already completed')

    question = None
    for item in attempt.test.test_questions:
        if item.question_id == payload.question_id:
            question = item.question
            break
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Question is not part of the attempt test')

    points = _get_question_points(attempt.test, payload.question_id)
    correct_option_ids = _get_correct_option_ids(question)
    selected_option_ids = set(payload.selected_option_ids or [])

    if question.question_type == 'text':
        normalized = (payload.text_answer or '').strip().lower()
        valid_answers = {option.text.strip().lower() for option in question.answer_options if option.is_correct}
        is_correct = normalized in valid_answers and normalized != ''
    else:
        existing_option_ids = {option.id for option in question.answer_options}
        if not selected_option_ids.issubset(existing_option_ids):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='One or more answer options are invalid')
        is_correct = selected_option_ids == correct_option_ids

    student_answer = db.scalar(
        select(models.StudentAnswer)
        .options(joinedload(models.StudentAnswer.selected_options))
        .where(
            models.StudentAnswer.attempt_id == attempt_id,
            models.StudentAnswer.question_id == payload.question_id,
        )
    )
    if not student_answer:
        student_answer = models.StudentAnswer(attempt_id=attempt_id, question_id=payload.question_id)
        db.add(student_answer)
        db.flush()
    else:
        for selected in list(student_answer.selected_options):
            db.delete(selected)
        db.flush()

    student_answer.text_answer = payload.text_answer
    student_answer.is_correct = is_correct
    student_answer.awarded_points = points if is_correct else 0

    for option_id in selected_option_ids:
        db.add(models.StudentAnswerOption(student_answer_id=student_answer.id, answer_option_id=option_id))

    db.commit()
    db.refresh(student_answer)

    return schemas.AnswerSubmitResponse(
        student_answer_id=student_answer.id,
        question_id=student_answer.question_id,
        is_correct=bool(student_answer.is_correct),
        awarded_points=student_answer.awarded_points or 0,
    )


def finish_attempt(db: Session, attempt_id: int):
    attempt = db.scalar(
        select(models.Attempt)
        .options(
            joinedload(models.Attempt.test).joinedload(models.Test.test_questions),
            joinedload(models.Attempt.test).joinedload(models.Test.topic),
            joinedload(models.Attempt.student_answers),
        )
        .where(models.Attempt.id == attempt_id)
    )
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Attempt not found')
    if attempt.completed_at:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Attempt is already completed')

    max_score = sum(item.points for item in attempt.test.test_questions)
    score = sum(answer.awarded_points or 0 for answer in attempt.student_answers)
    percentage = round((score / max_score) * 100, 2) if max_score else 0.0

    if percentage >= 85:
        recommendation_text = (
            f'Отличный результат по теме "{attempt.test.topic.title}". '
            'Рекомендуется адаптивный тест повышенной сложности.'
        )
    elif percentage >= 60:
        recommendation_text = (
            f'Хороший базовый уровень по теме "{attempt.test.topic.title}". '
            'Повторите вопросы, в которых были ошибки, и затем пройдите адаптивный тест.'
        )
    else:
        recommendation_text = (
            f'Есть пробелы по теме "{attempt.test.topic.title}". '
            'Рекомендуется повторить теорию и пройти адаптивный тест с более простыми вопросами.'
        )

    attempt.score = Decimal(str(round(score, 2)))
    attempt.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)

    recommendation = models.Recommendation(
        student_id=attempt.student_id,
        topic_id=attempt.test.topic_id,
        attempt_id=attempt.id,
        text=recommendation_text,
    )
    db.add(recommendation)
    db.commit()

    return schemas.FinishAttemptResponse(
        attempt_id=attempt.id,
        score=float(score),
        max_score=max_score,
        percentage=percentage,
        recommendation=recommendation_text,
    )


def generate_adaptive_test(db: Session, payload: schemas.AdaptiveTestGenerate):
    student = db.get(models.User, payload.student_id)
    topic = db.get(models.Topic, payload.topic_id)
    creator = db.get(models.User, payload.created_by)
    based_attempt = db.scalar(
        select(models.Attempt)
        .options(joinedload(models.Attempt.test), joinedload(models.Attempt.student_answers))
        .where(models.Attempt.id == payload.based_on_attempt_id)
    )

    if not student or not topic or not creator or not based_attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Student, topic, creator or attempt not found')

    wrong_question_ids = [answer.question_id for answer in based_attempt.student_answers if answer.is_correct is False]
    wrong_question_ids = list(dict.fromkeys(wrong_question_ids))

    topic_questions = db.scalars(
        select(models.Question)
        .where(models.Question.topic_id == payload.topic_id)
        .order_by(models.Question.difficulty.asc(), models.Question.id.asc())
    ).all()
    if not topic_questions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No questions found for topic')

    wrong_questions = [question for question in topic_questions if question.id in wrong_question_ids]
    remaining_questions = [question for question in topic_questions if question.id not in wrong_question_ids]

    percentage = float(based_attempt.score or 0)
    if based_attempt.test and based_attempt.test.test_questions:
        max_score = sum(item.points for item in based_attempt.test.test_questions)
        percentage = (float(based_attempt.score or 0) / max_score) * 100 if max_score else 0

    if percentage < 60:
        remaining_questions.sort(key=lambda q: (q.difficulty, q.id))
    else:
        remaining_questions.sort(key=lambda q: (-q.difficulty, q.id))

    selected_questions = (wrong_questions + remaining_questions)[: payload.question_count]
    if not selected_questions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Unable to build adaptive test')

    adaptive_test = models.Test(
        title=f'Адаптивный тест по теме: {topic.title}',
        topic_id=topic.id,
        created_by=creator.id,
        is_adaptive=True,
    )
    db.add(adaptive_test)
    db.flush()

    for order_no, question in enumerate(selected_questions, start=1):
        points = 1 if question.difficulty <= 2 else 2
        db.add(
            models.TestQuestion(
                test_id=adaptive_test.id,
                question_id=question.id,
                order_no=order_no,
                points=points,
            )
        )

    db.commit()
    return schemas.AdaptiveTestResponse(
        test_id=adaptive_test.id,
        title=adaptive_test.title,
        selected_question_ids=[question.id for question in selected_questions],
    )


def list_recommendations_for_student(db: Session, student_id: int):
    return db.scalars(
        select(models.Recommendation)
        .where(models.Recommendation.student_id == student_id)
        .order_by(models.Recommendation.created_at.desc(), models.Recommendation.id.desc())
    ).all()
