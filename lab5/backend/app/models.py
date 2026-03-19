from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

    users = relationship('User', back_populates='role')


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)

    role = relationship('Role', back_populates='users')
    created_tests = relationship('Test', back_populates='creator', foreign_keys='Test.created_by')
    attempts = relationship('Attempt', back_populates='student')
    recommendations = relationship('Recommendation', back_populates='student')


class Topic(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    questions = relationship('Question', back_populates='topic')
    tests = relationship('Test', back_populates='topic')
    recommendations = relationship('Recommendation', back_populates='topic')


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)
    difficulty = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint('difficulty BETWEEN 1 AND 5', name='questions_difficulty_check'),
    )

    topic = relationship('Topic', back_populates='questions')
    answer_options = relationship('AnswerOption', back_populates='question', cascade='all, delete-orphan')
    test_questions = relationship('TestQuestion', back_populates='question')
    student_answers = relationship('StudentAnswer', back_populates='question')


class AnswerOption(Base):
    __tablename__ = 'answer_options'

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)

    question = relationship('Question', back_populates='answer_options')
    selected_in_answers = relationship('StudentAnswerOption', back_populates='answer_option')


class Test(Base):
    __tablename__ = 'tests'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_adaptive = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    topic = relationship('Topic', back_populates='tests')
    creator = relationship('User', back_populates='created_tests', foreign_keys=[created_by])
    test_questions = relationship('TestQuestion', back_populates='test', cascade='all, delete-orphan')
    attempts = relationship('Attempt', back_populates='test')


class TestQuestion(Base):
    __tablename__ = 'test_questions'

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    order_no = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False, default=1)

    __table_args__ = (
        UniqueConstraint('test_id', 'question_id', name='uq_test_question'),
    )

    test = relationship('Test', back_populates='test_questions')
    question = relationship('Question', back_populates='test_questions')


class Attempt(Base):
    __tablename__ = 'attempts'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    completed_at = Column(DateTime)
    score = Column(Numeric(5, 2), default=0)

    student = relationship('User', back_populates='attempts')
    test = relationship('Test', back_populates='attempts')
    student_answers = relationship('StudentAnswer', back_populates='attempt', cascade='all, delete-orphan')
    recommendations = relationship('Recommendation', back_populates='attempt')


class StudentAnswer(Base):
    __tablename__ = 'student_answers'

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey('attempts.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    text_answer = Column(Text)
    is_correct = Column(Boolean)
    awarded_points = Column(Integer, default=0)

    attempt = relationship('Attempt', back_populates='student_answers')
    question = relationship('Question', back_populates='student_answers')
    selected_options = relationship('StudentAnswerOption', back_populates='student_answer', cascade='all, delete-orphan')


class StudentAnswerOption(Base):
    __tablename__ = 'student_answer_options'

    id = Column(Integer, primary_key=True, index=True)
    student_answer_id = Column(Integer, ForeignKey('student_answers.id'), nullable=False)
    answer_option_id = Column(Integer, ForeignKey('answer_options.id'), nullable=False)

    student_answer = relationship('StudentAnswer', back_populates='selected_options')
    answer_option = relationship('AnswerOption', back_populates='selected_in_answers')


class Recommendation(Base):
    __tablename__ = 'recommendations'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    attempt_id = Column(Integer, ForeignKey('attempts.id'), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    student = relationship('User', back_populates='recommendations')
    topic = relationship('Topic', back_populates='recommendations')
    attempt = relationship('Attempt', back_populates='recommendations')
