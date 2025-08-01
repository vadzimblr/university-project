import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

required_env_vars = ["POSTGRESQL_HOST", "POSTGRESQL_USER", "POSTGRESQL_PASSWORD", "POSTGRESQL_DB","POSTGRESQL_PORT"]
for var in required_env_vars:
    if not os.getenv(var):
        raise RuntimeError(f"Missing required environment variable: {var}")

POSTGRESQL_HOST = os.environ["POSTGRESQL_HOST"]
POSTGRESQL_USER = os.environ["POSTGRESQL_USER"]
POSTGRESQL_PASSWORD = os.environ["POSTGRESQL_PASSWORD"]
POSTGRESQL_DB = os.environ["POSTGRESQL_DB"]
POSTGRESQL_PORT = os.environ["POSTGRESQL_PORT"]

DATABASE_URL = f"postgresql://{POSTGRESQL_USER}:{POSTGRESQL_PASSWORD}@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DB}"

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_database_url():
    return DATABASE_URL
