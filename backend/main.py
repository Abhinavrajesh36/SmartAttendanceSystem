"""
SMART ATTENDANCE SYSTEM — LIVENESS DETECTION REMOVED
=====================================================

Pipeline (registration and attendance use IDENTICAL steps):
  1. enhance_image(frame)
  2. detector.detect_with_kps(full_frame)  — RetinaFace on full frame
  3. insightface_align(full_frame, kps)    — norm_crop -> 112x112
  4. recognizer.get_embedding(aligned)     — ArcFace get_feat on aligned crop
  5. FAISS cosine search -> mark attendance
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile, Form, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import numpy as np
import cv2
import torch
from datetime import datetime, date
from fastapi.responses import StreamingResponse
import pandas as pd
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

from backend.models.face_recognizer import RetinaFaceDetector, ArcFaceRecognizer, insightface_align
from backend.database.db_manager import DatabaseManager, get_db, SessionLocal
from backend.database.faiss_index import FAISSIndexManager
from backend.utils.preprocessing import preprocess_frame, enhance_image
from backend.schemas import AttendanceResponse

app = FastAPI(title="Smart Attendance System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

face_detector   = None
face_recognizer = None
faiss_manager   = None
db_manager      = None

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)

# ArcFace cosine distance threshold:
#   Same person  : 0.10 – 0.35
#   Diff person  : 0.45 – 0.90
RECOGNITION_THRESHOLD = 0.40


# =========================================================
# HELPER: rebuild FAISS from DB
# =========================================================
def rebuild_faiss_from_db(db: Session) -> int:
    global faiss_manager
    users = db_manager.get_all_users(db)
    faiss_manager.clear()
    rebuilt = 0
    for user in users:
        if user.face_embedding:
            emb = np.array(user.face_embedding, dtype="float32")
            faiss_manager.add_embedding(user.id, emb)
            rebuilt += 1
    faiss_manager.save_index()
    print(f"[FAISS] Rebuilt: {rebuilt} embeddings for {len(users)} users")
    return rebuilt


# =========================================================
# STARTUP
# =========================================================
@app.on_event("startup")
async def startup_event():
    global face_detector, face_recognizer, faiss_manager, db_manager

    device = "cuda" if torch.cuda.is_available() else "cpu"

    face_detector   = RetinaFaceDetector(device=device)
    face_recognizer = ArcFaceRecognizer(device=device)
    faiss_manager   = FAISSIndexManager(512, "data/faiss_index.bin")
    db_manager      = DatabaseManager()

    db = SessionLocal()
    try:
        rebuild_faiss_from_db(db)
    finally:
        db.close()

    print("System Ready")


# =========================================================
# REPORT HELPER
# =========================================================
def build_report_df(db: Session, report_date: date) -> pd.DataFrame:
    users   = db_manager.get_all_users(db)
    date_dt = datetime(report_date.year, report_date.month, report_date.day)
    rows = []
    for user in users:
        record = db_manager.get_attendance_by_user_and_date(db, user.id, date_dt)
        rows.append({
            "Employee ID":      user.employee_id,
            "Name":             user.name,
            "Department":       user.department,
            "Date":             report_date.strftime("%Y-%m-%d"),
            "Status":           "Present" if record else "Absent",
            "Check-In Time":    record.timestamp.strftime("%H:%M:%S") if record else "-",
            "Confidence Score": f"{record.confidence_score * 100:.2f}%" if record else "-",
        })
    df = pd.DataFrame(rows)
    return df.sort_values(by=["Department", "Name"])


# =========================================================
# SHARED: detect face + align on full frame
# =========================================================
def _detect_and_align(frame: np.ndarray):
    """
    Detect largest face in frame using RetinaFace,
    then produce an aligned 112x112 crop via InsightFace norm_crop.

    Returns (bbox, aligned_face) or (None, None) if no face found.
    """
    detections = face_detector.detect_with_kps(frame)
    if not detections:
        return None, None
    bbox, kps = detections[0]   # largest face first
    aligned = insightface_align(frame, kps)
    return bbox, aligned


# =========================================================
# REGISTER USER
# =========================================================
@app.post("/api/register")
async def register_user(
    name:        str              = Form(...),
    employee_id: str              = Form(...),
    department:  str              = Form(...),
    files:       List[UploadFile] = File(...),
    db:          Session          = Depends(get_db),
):
    if len(files) < 3:
        return {"status": "failed", "message": "Upload at least 3 images"}

    embeddings = []
    skipped    = 0

    for file in files:
        contents = await file.read()
        frame = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            skipped += 1
            continue

        frame = enhance_image(frame)

        bbox, aligned = _detect_and_align(frame)
        if aligned is None:
            print(f"[Register] No face in {file.filename} — skipping")
            skipped += 1
            continue

        embedding = face_recognizer.get_embedding(aligned)
        if np.linalg.norm(embedding) < 1e-6:
            print(f"[Register] Zero embedding for {file.filename} — skipping")
            skipped += 1
            continue

        embeddings.append(embedding)

    if len(embeddings) < 3:
        return {
            "status":  "failed",
            "message": (
                f"Need 3+ clear face images (got {len(embeddings)}, skipped {skipped}). "
                "Ensure good lighting and face is fully visible."
            ),
        }

    # Average then re-normalise onto unit hypersphere
    avg  = np.mean(embeddings, axis=0)
    norm = np.linalg.norm(avg)
    avg  = avg / norm if norm > 1e-6 else avg

    print(f"[Register] {len(embeddings)} embeddings averaged. Norm: {np.linalg.norm(avg):.6f}")

    user_id = db_manager.create_user(db, name, employee_id, department, avg.tolist())
    rebuild_faiss_from_db(db)

    return {
        "status":      "success",
        "user_id":     user_id,
        "images_used": len(embeddings),
        "skipped":     skipped,
    }


# =========================================================
# MARK ATTENDANCE
# =========================================================
@app.post("/api/mark-attendance", response_model=AttendanceResponse)
async def mark_attendance(
    file: UploadFile = File(...),
    db:   Session    = Depends(get_db),
):
    contents = await file.read()
    frame = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)

    if frame is None:
        return AttendanceResponse(status="failed", message="Invalid image", recognized=False)

    frame = preprocess_frame(frame)
    frame = enhance_image(frame)

    bbox, aligned = _detect_and_align(frame)
    if aligned is None:
        return AttendanceResponse(status="failed", message="No face detected", recognized=False)

    # Get embedding — get_feat bypasses detection, runs only ArcFace backbone
    embedding = face_recognizer.get_embedding(aligned)

    if np.linalg.norm(embedding) < 1e-6:
        return AttendanceResponse(
            status="failed",
            message="Could not extract face embedding. Try better lighting.",
            recognized=False,
        )

    # FAISS search
    try:
        candidates = faiss_manager.search_top_k(embedding, k=5)
    except ValueError:
        return AttendanceResponse(
            status="failed",
            message="No registered users. Please register first.",
            recognized=False,
        )

    if not candidates:
        return AttendanceResponse(
            status="not_registered",
            message="Face not recognised. Please register.",
            recognized=False,
        )

    best_user_id, best_distance = candidates[0]

    print(
        f"[Recognition] top-5: " +
        ", ".join(f"uid={uid} d={d:.4f}" for uid, d in candidates[:5])
    )
    print(f"[Recognition] best uid={best_user_id} dist={best_distance:.4f} threshold={RECOGNITION_THRESHOLD}")

    if best_distance > RECOGNITION_THRESHOLD:
        return AttendanceResponse(
            status="not_registered",
            message="Face not recognised. Try better lighting or re-register.",
            recognized=False,
        )

    user = db_manager.get_user(db, best_user_id)
    if not user:
        faiss_manager.remove_embedding(best_user_id)
        faiss_manager.save_index()
        return AttendanceResponse(
            status="failed", message="Face data outdated. Please re-register.", recognized=False
        )

    confidence = round(1.0 - best_distance, 4)
    today      = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    existing   = db_manager.get_attendance_by_user_and_date(db, best_user_id, today)

    if existing:
        return AttendanceResponse(
            status="already_marked",
            message=f"Attendance already marked for {user.name}",
            recognized=True,
            user_id=best_user_id, name=user.name, employee_id=user.employee_id,
            department=user.department, timestamp=existing.timestamp,
            confidence_score=confidence,
        )

    record = db_manager.create_attendance(db, best_user_id, confidence)
    return AttendanceResponse(
        status="success",
        message=f"Welcome {user.name}",
        recognized=True,
        user_id=best_user_id, name=user.name, employee_id=user.employee_id,
        department=user.department, timestamp=record.timestamp,
        confidence_score=confidence,
    )


# =========================================================
# GET ALL USERS
# =========================================================
@app.get("/api/users")
async def get_all_users(db: Session = Depends(get_db)):
    users = db_manager.get_all_users(db)
    return {
        "total": len(users),
        "users": [
            {
                "id": u.id, "name": u.name,
                "employee_id": u.employee_id, "department": u.department,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
    }


# =========================================================
# DELETE USER
# =========================================================
@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db_manager.get_user(db, user_id)
    if not user:
        return {"status": "failed", "message": f"User {user_id} not found"}
    user_name = user.name
    if not db_manager.delete_user(db, user_id):
        return {"status": "failed", "message": "Failed to delete user"}
    rebuild_faiss_from_db(db)
    return {"status": "success", "message": f"User '{user_name}' deleted", "user_id": user_id}


# =========================================================
# ADMIN: REBUILD FAISS
# =========================================================
@app.post("/api/admin/rebuild-faiss")
async def manual_rebuild_faiss(db: Session = Depends(get_db)):
    count = rebuild_faiss_from_db(db)
    return {"status": "success", "embeddings_loaded": count, "stats": faiss_manager.get_stats()}


# =========================================================
# DIAGNOSTIC
# =========================================================
@app.post("/api/debug/recognition-score")
async def debug_recognition_score(file: UploadFile = File(...)):
    contents = await file.read()
    frame = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        return {"error": "Invalid image"}

    frame = preprocess_frame(frame)
    frame = enhance_image(frame)

    bbox, aligned = _detect_and_align(frame)
    if aligned is None:
        return {"error": "No face detected"}

    embedding = face_recognizer.get_embedding(aligned)
    norm = np.linalg.norm(embedding)
    if norm < 1e-6:
        return {"error": "Zero embedding"}
    query = embedding / norm

    results = []
    for i, uid in enumerate(faiss_manager.id_mapping):
        try:
            stored = faiss_manager.index.reconstruct(i)
            sn = np.linalg.norm(stored)
            stored = stored / sn if sn > 1e-10 else stored
            cos_sim  = float(np.dot(query, stored))
            distance = 1.0 - cos_sim
            results.append({
                "user_id":    uid,
                "distance":   round(distance, 4),
                "confidence": round(cos_sim, 4),
                "would_pass": distance <= RECOGNITION_THRESHOLD,
            })
        except Exception:
            pass

    results.sort(key=lambda x: x["distance"])
    return {
        "total_in_index": faiss_manager.get_stats()["total_vectors"],
        "threshold":      RECOGNITION_THRESHOLD,
        "matches":        results,
    }


# =========================================================
# DASHBOARD
# =========================================================
@app.get("/api/stats/dashboard")
async def dashboard(db: Session = Depends(get_db)):
    users   = db_manager.get_all_users(db)
    today   = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    present = sum(1 for u in users if db_manager.get_attendance_by_user_and_date(db, u.id, today))
    total   = len(users)
    return {
        "total_registered_users": total,
        "present_today":          present,
        "absent_today":           total - present,
        "attendance_rate":        round(present / total * 100, 1) if total > 0 else 0.0,
        "faiss_stats":            faiss_manager.get_stats(),
    }


# =========================================================
# DOWNLOAD REPORT
# =========================================================
@app.get("/api/report/download")
async def download_report(
    report_date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    try:
        target_date = date.fromisoformat(report_date) if report_date else date.today()
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}
    df = build_report_df(db, target_date)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    filename = f"attendance_report_{target_date.strftime('%Y-%m-%d')}.csv"
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# =========================================================
# EMAIL REPORT
# =========================================================
@app.post("/api/report/send-email")
async def send_report_email(
    background_tasks: BackgroundTasks,
    recipient_email:  str           = Form(...),
    report_date:      Optional[str] = Form(default=None),
    db:               Session       = Depends(get_db),
):
    if not SMTP_USER or not SMTP_PASS:
        return {"status": "error", "message": "Email not configured."}
    try:
        target_date = date.fromisoformat(report_date) if report_date else date.today()
    except ValueError:
        return {"status": "error", "message": "Invalid date format. Use YYYY-MM-DD"}

    df            = build_report_df(db, target_date)
    buf           = io.StringIO()
    df.to_csv(buf, index=False)
    csv_bytes     = buf.getvalue().encode("utf-8")
    filename      = f"attendance_report_{target_date.strftime('%Y-%m-%d')}.csv"
    present_count = int((df["Status"] == "Present").sum())
    total_count   = len(df)
    rate          = round(present_count / total_count * 100, 1) if total_count > 0 else 0

    msg            = MIMEMultipart()
    msg["From"]    = SMTP_FROM
    msg["To"]      = recipient_email
    msg["Subject"] = f"Attendance Report — {target_date.strftime('%B %d, %Y')}"
    msg.attach(MIMEText(
        f"Attendance report for {target_date.strftime('%B %d, %Y')} attached.\n\n"
        f"Total: {total_count}  Present: {present_count}  "
        f"Absent: {total_count - present_count}  Rate: {rate}%",
        "plain"
    ))
    part = MIMEBase("application", "octet-stream")
    part.set_payload(csv_bytes)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={filename}")
    msg.attach(part)

    def send_mail():
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
                s.ehlo(); s.starttls(); s.login(SMTP_USER, SMTP_PASS)
                s.sendmail(SMTP_FROM, recipient_email, msg.as_string())
            print(f"Report emailed to {recipient_email}")
        except Exception as e:
            print(f"Email failed: {e}")

    background_tasks.add_task(send_mail)
    return {
        "status":  "success",
        "message": f"Report for {target_date.strftime('%B %d, %Y')} sending to {recipient_email}",
        "summary": {"total": total_count, "present": present_count,
                    "absent": total_count - present_count, "rate": rate},
    }
