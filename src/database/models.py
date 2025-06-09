from sqlalchemy import (
    Column, Integer, String, Date, Text, create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Resume(Base):
    __tablename__ = "resumes"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    resume_id        = Column(String, unique=True, nullable=False)   # your “ID” / file name
    resume_str       = Column(Text, nullable=False)
    resume_html      = Column(Text, nullable=False)
    category         = Column(String, nullable=False)

    # additional fields
    applicant_id     = Column(String, nullable=True)
    name             = Column(String, nullable=True)
    phone            = Column(String, nullable=True)
    birthdate        = Column(Date,   nullable=True)
    address          = Column(String, nullable=True)
    job_history      = Column(Text,   nullable=True)
    education        = Column(Text,   nullable=True)
    skills           = Column(Text,   nullable=True)
    cv_file_name     = Column(String, nullable=False)

# create an engine and session factory
engine = create_engine("sqlite:///resumes.db", echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def init_db():
    Base.metadata.create_all(bind=engine)
