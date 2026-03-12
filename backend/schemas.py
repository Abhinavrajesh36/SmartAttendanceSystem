"""
Pydantic Schemas for API Request/Response Models
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UserRegistration(BaseModel):
    """User registration request"""
    name: str = Field(..., min_length=2, max_length=100)
    employee_id: str = Field(..., min_length=3, max_length=50)
    department: str = Field(..., min_length=2, max_length=100)


class UserResponse(BaseModel):
    """User response model"""
    id: int
    name: str
    employee_id: str
    department: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AttendanceRecord(BaseModel):
    """Attendance record model"""
    id: int
    user_id: int
    timestamp: datetime
    confidence_score: float
    location: Optional[str] = None
    
    class Config:
        from_attributes = True


class AttendanceResponse(BaseModel):
    """Response for attendance marking"""
    status: str
    message: str
    recognized: bool
    user_id: Optional[int] = None
    name: Optional[str] = None
    employee_id: Optional[str] = None
    department: Optional[str] = None
    timestamp: Optional[datetime] = None
    liveness_passed: Optional[bool] = None
    confidence_score: Optional[float] = None


class RecognitionResult(BaseModel):
    """Face recognition result"""
    user_id: Optional[int] = None
    confidence: float
    is_live: bool
    detection_time_ms: float
    recognition_time_ms: float


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_registered_users: int
    present_today: int
    absent_today: int
    attendance_rate: float
    timestamp: datetime


class AttendanceHistoryRequest(BaseModel):
    """Request for attendance history"""
    user_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100


class AttendanceHistoryResponse(BaseModel):
    """Response for attendance history"""
    total_records: int
    records: List[AttendanceRecord]


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: str
    timestamp: datetime
