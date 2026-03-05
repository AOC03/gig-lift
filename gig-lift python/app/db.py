# Used ChatGPT to set up create db.py, i prompted it "create the code to set up an SQLAlchemy database connection for a carpooling app"
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:////home/AOC03/gig-lift/gig-lift python/carpool.db"
)

engine_kwargs = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update(dict(pool_size=5, max_overflow=10))

engine = create_engine(DATABASE_URL, **engine_kwargs)

class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


