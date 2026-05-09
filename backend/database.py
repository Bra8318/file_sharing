from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import settings

database_url = settings.db_url
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit = False,autoflush = False,bind = engine)
Base = declarative_base()

def connect_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()