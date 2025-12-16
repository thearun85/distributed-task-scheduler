from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = None
Session = None

class Base(DeclarativeBase):
    pass

def init_db(database_url):
    global engine, Session
    engine = create_engine(database_url, pool_size=5, max_overflow=10, pool_pre_ping=True)

    Session = sessionmaker(bind=engine)

def get_session():
    if Session is None:
        raise RuntimeError("Database is not yet initialized. Call init_db first.")
    return Session()
