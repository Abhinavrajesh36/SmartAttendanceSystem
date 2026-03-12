"""
Database Manager for Smart Attendance System
(PostgreSQL + SQLAlchemy ORM) - SAFE VERSION
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
from typing import List, Optional
import os

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://attendance_user:attendance_pass@localhost:5432/attendance_db"
)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# =========================================================
# MODELS
# =========================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    department = Column(String(100), nullable=False)
    face_embedding = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    attendance_records = relationship("Attendance", back_populates="user", cascade="all, delete-orphan")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    confidence_score = Column(Float, nullable=False)
    location = Column(String(200), nullable=True)

    user = relationship("User", back_populates="attendance_records")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    user_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


# =========================================================
# DATABASE MANAGER
# =========================================================

class DatabaseManager:

    def __init__(self):
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables ready")

    # ---------------- USER ----------------

    def create_user(self, db: Session, name: str, employee_id: str, department: str, face_embedding: list) -> int:
        employee_id = employee_id.lower().strip()
        user = db.query(User).filter(User.employee_id == employee_id).first()

        if user:
            user.name = name
            user.department = department
            user.face_embedding = face_embedding
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
            return user.id

        new_user = User(
            name=name,
            employee_id=employee_id,
            department=department,
            face_embedding=face_embedding
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user.id

    def get_user(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    def get_all_users(self, db: Session) -> List[User]:
        return db.query(User).all()

    def delete_user(self, db: Session, user_id: int) -> bool:
        """
        Delete a user and all their attendance records from the database.
        The cascade="all, delete-orphan" on the relationship handles
        attendance record deletion automatically.

        Returns True if deleted, False if user not found.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        self.log_event(db, "user_deleted", user_id, {
            "name": user.name,
            "employee_id": user.employee_id,
            "department": user.department
        })

        db.delete(user)
        db.commit()
        print(f"🗑️  Deleted user {user_id} ({user.name}) and their attendance records")
        return True

    # ---------------- ATTENDANCE ----------------

    def create_attendance(self, db: Session, user_id: int, confidence_score: float, location: Optional[str] = None):
        """
        SAFE attendance insert — prevents ForeignKeyViolation crash
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"⚠️ Attempted attendance for unknown user_id={user_id}")
            return None

        attendance = Attendance(
            user_id=user_id,
            confidence_score=confidence_score,
            location=location
        )

        db.add(attendance)
        db.commit()
        db.refresh(attendance)

        self.log_event(db, "attendance_marked", user_id, {"confidence": confidence_score})
        return attendance

    def get_attendance_by_user_and_date(self, db: Session, user_id: int, date: datetime):
        next_day = datetime(date.year, date.month, date.day, 23, 59, 59)
        return db.query(Attendance).filter(
            Attendance.user_id == user_id,
            Attendance.timestamp >= date,
            Attendance.timestamp <= next_day
        ).first()

    # ---------------- LOG ----------------

    def log_event(self, db: Session, event_type: str, user_id: Optional[int] = None, details: Optional[dict] = None):
        log = AuditLog(event_type=event_type, user_id=user_id, details=details)
        db.add(log)
        db.commit()


# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
