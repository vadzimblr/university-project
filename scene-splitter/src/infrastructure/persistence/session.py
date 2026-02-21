from sqlalchemy.orm import sessionmaker
from .engine import engine

SessionFactory = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
