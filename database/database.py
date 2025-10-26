from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.config import SQLALCHEMY_DATABASE_URL, BASE_DATABASE_URL

# 데이터베이스 생성용 엔진
init_engine = create_engine(BASE_DATABASE_URL)

# 데이터베이스 생성
with init_engine.connect() as connection:
    connection.execute(text("CREATE DATABASE IF NOT EXISTS `card-db`;"))

# 초기화 엔진 닫기
init_engine.dispose()

# 실제 사용할 SQLAlchemy 엔진
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
