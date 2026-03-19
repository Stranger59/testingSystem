import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./adaptive_testing.db')

connect_args = {'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {}

for _i in range(30):
    try:
        engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        break
    except Exception:
        print(f"DB not ready, retrying ({_i+1}/30)...")
        time.sleep(2)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
