from sqlalchemy import (
    Column, ForeignKey, Integer, String, Date, Text, text, create_engine
)
import os
import subprocess
from datetime import datetime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from ..config.config import DB_CONN

Base = declarative_base()

class ApplicantProfile(Base):
    __tablename__ = "ApplicantProfile"
    
    applicant_id     = Column(Integer, primary_key=True, autoincrement=True)
    first_name       = Column(String(50))
    last_name        = Column(String(50))
    date_of_birth    = Column(Date)
    address          = Column(String(255))
    phone_number     = Column(String(20))

    applications = relationship(
        "ApplicationDetail",
        back_populates="applicant",
        cascade="all, delete-orphan"
    )

class ApplicationDetail(Base):
    __tablename__ = "ApplicationDetail"
    detail_id        = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id     = Column(Integer, ForeignKey('ApplicantProfile.applicant_id'), nullable=False)
    application_role = Column(String(100))
    cv_path          = Column(Text)

    applicant = relationship("ApplicantProfile", back_populates="applications")



# create an engine and session factory
engine = create_engine(DB_CONN, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def init_db() -> bool:
    try:
        Base.metadata.create_all(bind=engine)
        # Test connection by executing a simple query
        with SessionLocal() as session:
            # Simple query just to verify connection works
            session.execute(text('SELECT 1'))
        print("Database initialized successfully!")
        return True
    except Exception as e:
        print(f"Database initialization failed: {str(e)}")
        return False

def dump_db(output_path=None, schema = True) -> bool:
    """
    Export the database to a SQL file
    """
    try:
        # Extract database configuration from connection string
        from urllib.parse import urlparse
        parsed = urlparse(DB_CONN)
        
        # Extract components from the connection string
        username = parsed.username
        password = parsed.password
        host = parsed.hostname
        port = parsed.port or 3306
        database = parsed.path.strip('/')
        
        # Default output path
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{database}_backup_{timestamp}.sql"
        
        # Build mysqldump command
        cmd = f"mysqldump -h {host} -P {port} -u {username} --password={password} {'-d' if schema else ''} --databases {database} > {output_path}"
        
        # Execute command
        process = subprocess.Popen(
            cmd,
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Export failed: {stderr.decode()}")
            return False
        
        print(f"Database {"schema " if schema else ""}exported successfully to: {output_path}")
        print(f"File size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")
        return True
    
    except Exception as e:
        print(f"Database export failed: {str(e)}")
        return False