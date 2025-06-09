from sqlalchemy import (
    Column, ForeignKey, Integer, String, Date, Text, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from config.config import DB_CONN

Base = declarative_base()

class ApplicantProfile(Base):
    __tablename__ = "ApplicantProfile"
    
    applicant_id     = Column(Integer, primary_key=True, autoincrement=True)
    first_name       = Column(String(50))
    last_name        = Column(String(50))
    birthdate        = Column(Date)
    address          = Column(String(255))
    phone            = Column(String(20))

    applications = relationship(
        "ApplicationDetail",
        back_populates="applicant",
        cascade="all, delete-orphan"
    )

class ApplicationDetail(Base):
    __tablename__ = "ApplicationDetail"
    detail_id        = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id     = Column(Integer, ForeignKey('applicant_profile.applicant_id'), nullable=False)
    applicant_role   = Column(String(100))
    cv_file_name     = Column(Text)

    applicant = relationship("ApplicantProfile", back_populates="applications")



# create an engine and session factory
engine = create_engine(DB_CONN, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized!")
