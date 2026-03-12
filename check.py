import torch
print("Torch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("GPU:", torch.cuda.get_device_name(0))


# # # # # """
# # # # # Smart Attendance System - Main Backend API
# # # # # FastAPI application with YOLOv9 + ArcFace + Liveness Detection
# # # # # """

# # # # # from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
# # # # # from fastapi.middleware.cors import CORSMiddleware
# # # # # from fastapi.responses import JSONResponse
# # # # # from sqlalchemy.orm import Session
# # # # # from typing import List, Optional
# # # # # import numpy as np
# # # # # import cv2
# # # # # import torch
# # # # # from datetime import datetime, timedelta
# # # # # import base64
# # # # # from io import BytesIO
# # # # # from PIL import Image

# # # # # # Import custom modules
# # # # # from backend.models.face_detector import YOLOv9FaceDetector
# # # # # from backend.models.face_recognizer import ArcFaceRecognizer
# # # # # from backend.models.liveness_detector import LivenessDetector
# # # # # from backend.database.db_manager import DatabaseManager, get_db
# # # # # from backend.database.faiss_index import FAISSIndexManager
# # # # # from backend.utils.face_alignment import align_face
# # # # # from backend.utils.preprocessing import preprocess_frame
# # # # # from backend.schemas import (
# # # # #     AttendanceRecord,
# # # # #     UserRegistration,
# # # # #     RecognitionResult,
# # # # #     AttendanceResponse
# # # # # )

# # # # # # Initialize FastAPI app
# # # # # app = FastAPI(
# # # # #     title="Smart Attendance System API",
# # # # #     description="Face Recognition based Attendance System with Anti-Spoofing",
# # # # #     version="1.0.0"
# # # # # )

# # # # # # CORS Configuration
# # # # # app.add_middleware(
# # # # #     CORSMiddleware,
# # # # #     allow_origins=["http://localhost:3000", "http://localhost:5173"],
# # # # #     allow_credentials=True,
# # # # #     allow_methods=["*"],
# # # # #     allow_headers=["*"],
# # # # # )

# # # # # # Global model instances
# # # # # face_detector = None
# # # # # face_recognizer = None
# # # # # liveness_detector = None
# # # # # faiss_manager = None
# # # # # db_manager = None

# # # # # @app.on_event("startup")
# # # # # async def startup_event():
# # # # #     """Initialize models and database on startup"""
# # # # #     global face_detector, face_recognizer, liveness_detector, faiss_manager, db_manager
    
# # # # #     print("🚀 Initializing Smart Attendance System...")
    
# # # # #     # Initialize YOLOv9 Face Detector
# # # # #     face_detector = YOLOv9FaceDetector(
# # # # #         model_path="weights/yolov9_face.pt",
# # # # #         conf_threshold=0.5,
# # # # #         device="cuda" if torch.cuda.is_available() else "cpu"
# # # # #     )
    
# # # # #     # Initialize ArcFace Recognizer
# # # # #     face_recognizer = ArcFaceRecognizer(
# # # # #         model_path="weights/arcface_r100.pth",
# # # # #         embedding_size=512,
# # # # #         device="cuda" if torch.cuda.is_available() else "cpu"
# # # # #     )
    
# # # # #     # Initialize Liveness Detector
# # # # #     liveness_detector = LivenessDetector(
# # # # #         model_path="weights/liveness_model.pth",
# # # # #         device="cuda" if torch.cuda.is_available() else "cpu"
# # # # #     )
    
# # # # #     # Initialize FAISS Index Manager
# # # # #     faiss_manager = FAISSIndexManager(
# # # # #         embedding_dim=512,
# # # # #         index_path="data/faiss_index.bin"
# # # # #     )
    
# # # # #     # Initialize Database Manager
# # # # #     db_manager = DatabaseManager()
    
# # # # #     print("✅ All systems initialized successfully!")

# # # # # @app.get("/")
# # # # # async def root():
# # # # #     """Health check endpoint"""
# # # # #     return {
# # # # #         "status": "active",
# # # # #         "service": "Smart Attendance System",
# # # # #         "version": "1.0.0",
# # # # #         "models": {
# # # # #             "face_detector": "YOLOv9",
# # # # #             "face_recognizer": "ArcFace",
# # # # #             "liveness_detector": "Active"
# # # # #         }
# # # # #     }

# # # # # @app.post("/api/register", response_model=dict)
# # # # # async def register_user(
# # # # #     name: str,
# # # # #     employee_id: str,
# # # # #     department: str,
# # # # #     files: List[UploadFile] = File(...),
# # # # #     db: Session = Depends(get_db)
# # # # # ):
# # # # #     """
# # # # #     Register a new user with multiple face images
# # # # #     Minimum 5 images recommended for better accuracy
# # # # #     """
# # # # #     try:
# # # # #         if len(files) < 3:
# # # # #             raise HTTPException(
# # # # #                 status_code=400,
# # # # #                 detail="Minimum 3 face images required for registration"
# # # # #             )
        
# # # # #         embeddings = []
        
# # # # #         for file in files:
# # # # #             # Read image
# # # # #             contents = await file.read()
# # # # #             nparr = np.frombuffer(contents, np.uint8)
# # # # #             frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
# # # # #             # Detect face
# # # # #             detections = face_detector.detect(frame)
            
# # # # #             if len(detections) == 0:
# # # # #                 continue
            
# # # # #             if len(detections) > 1:
# # # # #                 raise HTTPException(
# # # # #                     status_code=400,
# # # # #                     detail=f"Multiple faces detected in {file.filename}. Please use images with single face."
# # # # #                 )
            
# # # # #             # Get face bounding box
# # # # #             bbox = detections[0]
            
# # # # #             # Align face
# # # # #             aligned_face = align_face(frame, bbox)
            
# # # # #             # Check liveness (only for registration to ensure quality)
# # # # #             is_live = liveness_detector.predict(aligned_face)
# # # # #             if not is_live:
# # # # #                 raise HTTPException(
# # # # #                     status_code=400,
# # # # #                     detail=f"Possible spoofing detected in {file.filename}. Please use live images."
# # # # #                 )
            
# # # # #             # Generate embedding
# # # # #             embedding = face_recognizer.get_embedding(aligned_face)
# # # # #             embeddings.append(embedding)
        
# # # # #         if len(embeddings) < 3:
# # # # #             raise HTTPException(
# # # # #                 status_code=400,
# # # # #                 detail="Could not extract valid faces from enough images"
# # # # #             )
        
# # # # #         # Calculate average embedding
# # # # #         avg_embedding = np.mean(embeddings, axis=0)
        
# # # # #         # Store in database
# # # # #         user_id = db_manager.create_user(
# # # # #             db=db,
# # # # #             name=name,
# # # # #             employee_id=employee_id,
# # # # #             department=department,
# # # # #             face_embedding=avg_embedding.tolist()
# # # # #         )
        
# # # # #         # Add to FAISS index
# # # # #         faiss_manager.add_embedding(user_id, avg_embedding)
# # # # #         faiss_manager.save_index()
        
# # # # #         return {
# # # # #             "status": "success",
# # # # #             "message": f"User {name} registered successfully",
# # # # #             "user_id": user_id,
# # # # #             "embeddings_processed": len(embeddings)
# # # # #         }
        
# # # # #     except Exception as e:
# # # # #         raise HTTPException(status_code=500, detail=str(e))

# # # # # @app.post("/api/mark-attendance", response_model=AttendanceResponse)
# # # # # async def mark_attendance(
# # # # #     file: UploadFile = File(...),
# # # # #     db: Session = Depends(get_db)
# # # # # ):
# # # # #     """
# # # # #     Mark attendance by capturing a face image
# # # # #     Performs: Detection → Recognition → Liveness Check → Attendance Marking
# # # # #     """
# # # # #     try:
# # # # #         # Read and decode image
# # # # #         contents = await file.read()
# # # # #         nparr = np.frombuffer(contents, np.uint8)
# # # # #         frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
# # # # #         if frame is None:
# # # # #             raise HTTPException(status_code=400, detail="Invalid image format")
        
# # # # #         # Preprocess frame
# # # # #         frame = preprocess_frame(frame)
        
# # # # #         # Step 1: Face Detection with YOLOv9
# # # # #         detections = face_detector.detect(frame)
        
# # # # #         if len(detections) == 0:
# # # # #             return AttendanceResponse(
# # # # #                 status="failed",
# # # # #                 message="No face detected in the image",
# # # # #                 recognized=False
# # # # #             )
        
# # # # #         if len(detections) > 1:
# # # # #             return AttendanceResponse(
# # # # #                 status="failed",
# # # # #                 message=f"Multiple faces detected ({len(detections)}). Please ensure single person.",
# # # # #                 recognized=False
# # # # #             )
        
# # # # #         # Get face bounding box
# # # # #         bbox = detections[0]
        
# # # # #         # Step 2: Face Alignment
# # # # #         aligned_face = align_face(frame, bbox)
        
# # # # #         # Step 3: Liveness Detection (Anti-Spoofing)
# # # # #         is_live = liveness_detector.predict(aligned_face)
        
# # # # #         if not is_live:
# # # # #             return AttendanceResponse(
# # # # #                 status="failed",
# # # # #                 message="Liveness check failed. Possible spoofing attempt detected.",
# # # # #                 recognized=False,
# # # # #                 liveness_passed=False
# # # # #             )
        
# # # # #         # Step 4: Face Recognition (ArcFace Embedding)
# # # # #         embedding = face_recognizer.get_embedding(aligned_face)
        
# # # # #         # Step 5: FAISS Similarity Search
# # # # #         user_id, distance = faiss_manager.search(embedding, k=1)
        
# # # # #         # Threshold for recognition (lower distance = higher similarity)
# # # # #         RECOGNITION_THRESHOLD = 0.6
        
# # # # #         if distance > RECOGNITION_THRESHOLD:
# # # # #             return AttendanceResponse(
# # # # #                 status="failed",
# # # # #                 message="Face not recognized. Please register first.",
# # # # #                 recognized=False,
# # # # #                 liveness_passed=True
# # # # #             )
        
# # # # #         # Step 6: Fetch user details
# # # # #         user = db_manager.get_user(db, user_id)
        
# # # # #         if not user:
# # # # #             return AttendanceResponse(
# # # # #                 status="failed",
# # # # #                 message="User data not found",
# # # # #                 recognized=False
# # # # #             )
        
# # # # #         # Step 7: Check if already marked today
# # # # #         today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
# # # # #         existing_attendance = db_manager.get_attendance_by_user_and_date(
# # # # #             db, user_id, today_start
# # # # #         )
        
# # # # #         if existing_attendance:
# # # # #             return AttendanceResponse(
# # # # #                 status="already_marked",
# # # # #                 message=f"Attendance already marked for {user.name} today at {existing_attendance.timestamp.strftime('%I:%M %p')}",
# # # # #                 recognized=True,
# # # # #                 user_id=user_id,
# # # # #                 name=user.name,
# # # # #                 employee_id=user.employee_id,
# # # # #                 department=user.department,
# # # # #                 timestamp=existing_attendance.timestamp,
# # # # #                 liveness_passed=True,
# # # # #                 confidence_score=float(1 - distance)
# # # # #             )
        
# # # # #         # Step 8: Mark Attendance
# # # # #         attendance_record = db_manager.create_attendance(
# # # # #             db=db,
# # # # #             user_id=user_id,
# # # # #             confidence_score=float(1 - distance)
# # # # #         )
        
# # # # #         return AttendanceResponse(
# # # # #             status="success",
# # # # #             message=f"Attendance marked successfully for {user.name}",
# # # # #             recognized=True,
# # # # #             user_id=user_id,
# # # # #             name=user.name,
# # # # #             employee_id=user.employee_id,
# # # # #             department=user.department,
# # # # #             timestamp=attendance_record.timestamp,
# # # # #             liveness_passed=True,
# # # # #             confidence_score=float(1 - distance)
# # # # #         )
        
# # # # #     except Exception as e:
# # # # #         raise HTTPException(status_code=500, detail=f"Error processing attendance: {str(e)}")

# # # # # @app.get("/api/attendance/today")
# # # # # async def get_today_attendance(db: Session = Depends(get_db)):
# # # # #     """Get all attendance records for today"""
# # # # #     try:
# # # # #         today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
# # # # #         records = db_manager.get_attendance_by_date_range(
# # # # #             db, today_start, datetime.now()
# # # # #         )
        
# # # # #         return {
# # # # #             "status": "success",
# # # # #             "date": today_start.strftime("%Y-%m-%d"),
# # # # #             "total_present": len(records),
# # # # #             "records": [
# # # # #                 {
# # # # #                     "id": r.id,
# # # # #                     "user_id": r.user_id,
# # # # #                     "name": r.user.name,
# # # # #                     "employee_id": r.user.employee_id,
# # # # #                     "department": r.user.department,
# # # # #                     "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
# # # # #                     "confidence_score": r.confidence_score
# # # # #                 }
# # # # #                 for r in records
# # # # #             ]
# # # # #         }
# # # # #     except Exception as e:
# # # # #         raise HTTPException(status_code=500, detail=str(e))

# # # # # @app.get("/api/attendance/user/{user_id}")
# # # # # async def get_user_attendance_history(
# # # # #     user_id: int,
# # # # #     days: int = 30,
# # # # #     db: Session = Depends(get_db)
# # # # # ):
# # # # #     """Get attendance history for a specific user"""
# # # # #     try:
# # # # #         end_date = datetime.now()
# # # # #         start_date = end_date - timedelta(days=days)
        
# # # # #         records = db_manager.get_user_attendance(db, user_id, start_date, end_date)
        
# # # # #         return {
# # # # #             "status": "success",
# # # # #             "user_id": user_id,
# # # # #             "records": [
# # # # #                 {
# # # # #                     "date": r.timestamp.strftime("%Y-%m-%d"),
# # # # #                     "time": r.timestamp.strftime("%H:%M:%S"),
# # # # #                     "confidence_score": r.confidence_score
# # # # #                 }
# # # # #                 for r in records
# # # # #             ]
# # # # #         }
# # # # #     except Exception as e:
# # # # #         raise HTTPException(status_code=500, detail=str(e))

# # # # # @app.get("/api/users")
# # # # # async def get_all_users(db: Session = Depends(get_db)):
# # # # #     """Get all registered users"""
# # # # #     try:
# # # # #         users = db_manager.get_all_users(db)
        
# # # # #         return {
# # # # #             "status": "success",
# # # # #             "total_users": len(users),
# # # # #             "users": [
# # # # #                 {
# # # # #                     "id": u.id,
# # # # #                     "name": u.name,
# # # # #                     "employee_id": u.employee_id,
# # # # #                     "department": u.department,
# # # # #                     "registered_at": u.created_at.strftime("%Y-%m-%d %H:%M:%S")
# # # # #                 }
# # # # #                 for u in users
# # # # #             ]
# # # # #         }
# # # # #     except Exception as e:
# # # # #         raise HTTPException(status_code=500, detail=str(e))

# # # # # @app.delete("/api/user/{user_id}")
# # # # # async def delete_user(user_id: int, db: Session = Depends(get_db)):
# # # # #     """Delete a user from the system"""
# # # # #     try:
# # # # #         # Remove from FAISS index
# # # # #         faiss_manager.remove_embedding(user_id)
# # # # #         faiss_manager.save_index()
        
# # # # #         # Remove from database
# # # # #         db_manager.delete_user(db, user_id)
        
# # # # #         return {
# # # # #             "status": "success",
# # # # #             "message": f"User {user_id} deleted successfully"
# # # # #         }
# # # # #     except Exception as e:
# # # # #         raise HTTPException(status_code=500, detail=str(e))

# # # # # @app.get("/api/stats/dashboard")
# # # # # async def get_dashboard_stats(db: Session = Depends(get_db)):
# # # # #     """Get dashboard statistics"""
# # # # #     try:
# # # # #         total_users = db_manager.count_total_users(db)
        
# # # # #         today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
# # # # #         today_attendance = db_manager.get_attendance_by_date_range(
# # # # #             db, today_start, datetime.now()
# # # # #         )
        
# # # # #         # Calculate attendance rate
# # # # #         attendance_rate = (len(today_attendance) / total_users * 100) if total_users > 0 else 0
        
# # # # #         return {
# # # # #             "status": "success",
# # # # #             "total_registered_users": total_users,
# # # # #             "present_today": len(today_attendance),
# # # # #             "absent_today": total_users - len(today_attendance),
# # # # #             "attendance_rate": round(attendance_rate, 2),
# # # # #             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# # # # #         }
# # # # #     except Exception as e:
# # # # #         raise HTTPException(status_code=500, detail=str(e))

# # # # # @app.post("/api/test/liveness")
# # # # # async def test_liveness(file: UploadFile = File(...)):
# # # # #     """Test endpoint for liveness detection"""
# # # # #     try:
# # # # #         contents = await file.read()
# # # # #         nparr = np.frombuffer(contents, np.uint8)
# # # # #         frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
# # # # #         detections = face_detector.detect(frame)
# # # # #         if len(detections) == 0:
# # # # #             return {"status": "no_face", "is_live": False}
        
# # # # #         bbox = detections[0]
# # # # #         aligned_face = align_face(frame, bbox)
# # # # #         is_live = liveness_detector.predict(aligned_face)
        
# # # # #         return {
# # # # #             "status": "success",
# # # # #             "is_live": is_live,
# # # # #             "message": "Real person detected" if is_live else "Spoofing attempt detected"
# # # # #         }
# # # # #     except Exception as e:
# # # # #         raise HTTPException(status_code=500, detail=str(e))

# # # # # if __name__ == "__main__":
# # # # #     import uvicorn
# # # # #     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
# # # """
# # # # Smart Attendance System - Main Backend API (STABLE VERSION)
# # # # YOLOv9 + ArcFace + Soft Liveness + Auto Face Selection
# # # # """

# # # # from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
# # # # from fastapi.middleware.cors import CORSMiddleware
# # # # from sqlalchemy.orm import Session
# # # # from typing import List
# # # # import numpy as np
# # # # import cv2
# # # # import torch
# # # # from datetime import datetime, timedelta

# # # # # Modules
# # # # from backend.models.face_detector import YOLOv9FaceDetector
# # # # from backend.models.face_recognizer import ArcFaceRecognizer
# # # # from backend.models.liveness_detector import LivenessDetector
# # # # from backend.database.db_manager import DatabaseManager, get_db
# # # # from backend.database.faiss_index import FAISSIndexManager
# # # # from backend.utils.face_alignment import align_face
# # # # from backend.utils.preprocessing import preprocess_frame
# # # # from backend.schemas import AttendanceResponse

# # # # app = FastAPI(title="Smart Attendance System")

# # # # app.add_middleware(
# # # #     CORSMiddleware,
# # # #     allow_origins=["*"],
# # # #     allow_credentials=True,
# # # #     allow_methods=["*"],
# # # #     allow_headers=["*"],
# # # # )

# # # # face_detector=None
# # # # face_recognizer=None
# # # # liveness_detector=None
# # # # faiss_manager=None
# # # # db_manager=None


# # # # # --------------------------------------------------
# # # # # Startup
# # # # # --------------------------------------------------
# # # # @app.on_event("startup")
# # # # async def startup_event():
# # # #     global face_detector, face_recognizer, liveness_detector, faiss_manager, db_manager

# # # #     print("🚀 Initializing System")

# # # #     face_detector = YOLOv9FaceDetector(
# # # #         model_path="weights/yolov9_face.pt",
# # # #         device="cuda" if torch.cuda.is_available() else "cpu"
# # # #     )

# # # #     face_recognizer = ArcFaceRecognizer(
# # # #         model_path="weights/arcface_r100.pth",
# # # #         device="cuda" if torch.cuda.is_available() else "cpu"
# # # #     )

# # # #     liveness_detector = LivenessDetector(
# # # #         model_path="weights/liveness_model.pth",
# # # #         device="cuda" if torch.cuda.is_available() else "cpu"
# # # #     )

# # # #     faiss_manager = FAISSIndexManager(512,"data/faiss_index.bin")
# # # #     db_manager = DatabaseManager()

# # # #     # ---------------------------------------------
# # # #     # Rebuild FAISS index from database
# # # #     # ---------------------------------------------
# # # #     print("Loading registered faces into FAISS index...")

# # # #     db = next(get_db())

# # # #     users = db_manager.get_all_users(db)

# # # #     count = 0
# # # #     for user in users:
# # # #         if user.face_embedding:
# # # #             emb = np.array(user.face_embedding, dtype=np.float32)
# # # #             faiss_manager.add_embedding(user.id, emb)
# # # #             count += 1

# # # #     faiss_manager.save_index()

# # # #     print(f"Loaded {count} registered faces into FAISS")



# # # #     print("✅ System Ready")


# # # # # --------------------------------------------------
# # # # # Choose main face (largest)
# # # # # --------------------------------------------------
# # # # def select_primary_face(detections):
# # # #     if len(detections)==0:
# # # #         return None

# # # #     def area(b):
# # # #         x1,y1,x2,y2=b
# # # #         return (x2-x1)*(y2-y1)

# # # #     return sorted(detections,key=area,reverse=True)[0]


# # # # # --------------------------------------------------
# # # # # Attendance API
# # # # # --------------------------------------------------
# # # # @app.post("/api/mark-attendance",response_model=AttendanceResponse)
# # # # async def mark_attendance(file:UploadFile=File(...),db:Session=Depends(get_db)):

# # # #     try:
# # # #         contents=await file.read()
# # # #         frame=cv2.imdecode(np.frombuffer(contents,np.uint8),cv2.IMREAD_COLOR)

# # # #         if frame is None:
# # # #             raise HTTPException(400,"Invalid image")

# # # #         frame=preprocess_frame(frame)

# # # #         # Detect
# # # #         detections=face_detector.detect(frame)
# # # #         if len(detections)==0:
# # # #             return AttendanceResponse(status="failed",message="No face detected",recognized=False)

# # # #         bbox=select_primary_face(detections)

# # # #         # Align
# # # #         aligned=align_face(frame,bbox)

# # # #         # Liveness (soft)
# # # #         is_live=liveness_detector.predict(aligned)
# # # #         if not is_live:
# # # #             print("⚠️ Weak liveness — continuing")

# # # #         # Embedding
# # # #         emb=face_recognizer.get_embedding(aligned)

# # # #         # Search
# # # #         user_id,dist=faiss_manager.search(emb,k=1)

# # # #         THRESHOLD=0.50
# # # #         if dist>THRESHOLD:
# # # #             return AttendanceResponse(status="failed",message="Face not recognized",recognized=False,liveness_passed=is_live)

# # # #         user=db_manager.get_user(db,user_id)

# # # #         # Already marked
# # # #         today=datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
# # # #         existing=db_manager.get_attendance_by_user_and_date(db,user_id,today)

# # # #         if existing:
# # # #             return AttendanceResponse(
# # # #                 status="already_marked",
# # # #                 message="Attendance already marked",
# # # #                 recognized=True,
# # # #                 user_id=user_id,
# # # #                 name=user.name,
# # # #                 employee_id=user.employee_id,
# # # #                 department=user.department,
# # # #                 timestamp=existing.timestamp,
# # # #                 liveness_passed=is_live,
# # # #                 confidence_score=float(1-dist)
# # # #             )

# # # #         # Mark
# # # #         record=db_manager.create_attendance(db,user_id,float(1-dist))

# # # #         return AttendanceResponse(
# # # #             status="success",
# # # #             message=f"Welcome {user.name}",
# # # #             recognized=True,
# # # #             user_id=user_id,
# # # #             name=user.name,
# # # #             employee_id=user.employee_id,
# # # #             department=user.department,
# # # #             timestamp=record.timestamp,
# # # #             liveness_passed=is_live,
# # # #             confidence_score=float(1-dist)
# # # #         )

# # # #     except Exception as e:
# # # #         raise HTTPException(500,f"Error: {str(e)}")

# # # # # --------------------------------------------------
# # # # # REGISTER USER
# # # # # --------------------------------------------------
# # # # from fastapi import Form

# # # # @app.post("/api/register")
# # # # async def register_user(
# # # #     name: str = Form(...),
# # # #     employee_id: str = Form(...),
# # # #     department: str = Form(...),
# # # #     files: List[UploadFile] = File(...),
# # # #     db: Session = Depends(get_db)
# # # # ):

# # # #     try:
# # # #         if len(files) < 3:
# # # #             raise HTTPException(status_code=400, detail="Upload at least 3 images")

# # # #         embeddings = []

# # # #         for file in files:
# # # #             contents = await file.read()
# # # #             frame = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)

# # # #             if frame is None:
# # # #                 continue

# # # #             detections = face_detector.detect(frame)
# # # #             if len(detections) == 0:
# # # #                 continue

# # # #             # choose main face automatically
# # # #             bbox = select_primary_face(detections)
# # # #             aligned = align_face(frame, bbox)

# # # #             emb = face_recognizer.get_embedding(aligned)
# # # #             embeddings.append(emb)

# # # #         if len(embeddings) < 3:
# # # #             raise HTTPException(status_code=400, detail="Could not extract enough valid faces")

# # # #         # average embedding
# # # #         avg_embedding = np.mean(embeddings, axis=0)

# # # #         user_id = db_manager.create_user(
# # # #             db=db,
# # # #             name=name,
# # # #             employee_id=employee_id,
# # # #             department=department,
# # # #             face_embedding=avg_embedding.tolist()
# # # #         )

# # # #         faiss_manager.add_embedding(user_id, avg_embedding)
# # # #         faiss_manager.save_index()

# # # #         # store in DB
# # # #         user_id = db_manager.create_user(
# # # #             db=db,
# # # #             name=name,
# # # #             employee_id=employee_id,
# # # #             department=department,
# # # #             face_embedding=avg_embedding.tolist()
# # # #         )

# # # #         # add to FAISS
# # # #         faiss_manager.add_embedding(user_id, avg_embedding)
# # # #         faiss_manager.save_index()

# # # #         return {
# # # #             "status": "success",
# # # #             "message": f"{name} registered successfully",
# # # #             "user_id": user_id
# # # #         }

    
# # # #     except ValueError as e:
# # # #         raise HTTPException(status_code=400, detail=str(e))

# # # #     except Exception as e:
# # # #         raise HTTPException(status_code=500, detail="Registration failed")





# # # # # --------------------------------------------------
# # # # # Health
# # # # # --------------------------------------------------
# # # # @app.get("/")
# # # # async def root():
# # # #     return {"status":"running"}

# # # # @app.get("/api/stats/dashboard")
# # # # async def dashboard_stats(db: Session = Depends(get_db)):
# # # #     ...
# # # #     return {...}


# # # # # 👇 ALWAYS LAST
# # # # if __name__ == "__main__":
# # # #     import uvicorn
# # # #     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)




# # # """
# # # Smart Attendance System - Stable Backend API
# # # YOLOv9 + ArcFace + Liveness + Safe DB Handling
# # # """

# # # from fastapi import FastAPI, File, UploadFile, Depends
# # # from fastapi.middleware.cors import CORSMiddleware
# # # from sqlalchemy.orm import Session
# # # import numpy as np
# # # import cv2
# # # import torch
# # # from datetime import datetime

# # # # Modules
# # # from backend.models.face_detector import YOLOv9FaceDetector
# # # from backend.models.face_recognizer import ArcFaceRecognizer
# # # from backend.models.liveness_detector import LivenessDetector
# # # from backend.database.db_manager import DatabaseManager, get_db
# # # from backend.database.faiss_index import FAISSIndexManager
# # # from backend.utils.face_alignment import align_face
# # # from backend.utils.preprocessing import preprocess_frame
# # # from backend.schemas import AttendanceResponse

# # # # --------------------------------------------------
# # # # FastAPI setup
# # # # --------------------------------------------------
# # # app = FastAPI(title="Smart Attendance System")

# # # app.add_middleware(
# # #     CORSMiddleware,
# # #     allow_origins=["*"],
# # #     allow_credentials=True,
# # #     allow_methods=["*"],
# # #     allow_headers=["*"],
# # # )

# # # # Global instances
# # # face_detector = None
# # # face_recognizer = None
# # # liveness_detector = None
# # # faiss_manager = None
# # # db_manager = None


# # # # --------------------------------------------------
# # # # Startup
# # # # --------------------------------------------------
# # # @app.on_event("startup")
# # # async def startup_event():
# # #     global face_detector, face_recognizer, liveness_detector, faiss_manager, db_manager

# # #     print("🚀 Initializing system...")

# # #     device = "cuda" if torch.cuda.is_available() else "cpu"

# # #     face_detector = YOLOv9FaceDetector(
# # #         model_path="weights/yolov9_face.pt",
# # #         device=device
# # #     )

# # #     face_recognizer = ArcFaceRecognizer(
# # #         model_path="weights/arcface_r100.pth",
# # #         device=device
# # #     )

# # #     liveness_detector = LivenessDetector(
# # #         model_path="weights/liveness_model.pth",
# # #         device=device
# # #     )

# # #     faiss_manager = FAISSIndexManager(
# # #         embedding_dim=512,
# # #         index_path="data/faiss_index.bin"
# # #     )

# # #     db_manager = DatabaseManager()

# # #     print("✅ System ready!")


# # # # --------------------------------------------------
# # # # Attendance Endpoint
# # # # --------------------------------------------------
# # # @app.post("/api/mark-attendance", response_model=AttendanceResponse)
# # # async def mark_attendance(file: UploadFile = File(...), db: Session = Depends(get_db)):

# # #     try:
# # #         # Read image
# # #         contents = await file.read()
# # #         nparr = np.frombuffer(contents, np.uint8)
# # #         frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

# # #         if frame is None:
# # #             return AttendanceResponse(status="failed", message="Invalid image", recognized=False)

# # #         frame = preprocess_frame(frame)

# # #         # 1️⃣ Detect face
# # #         detections = face_detector.detect(frame)

# # #         if len(detections) == 0:
# # #             return AttendanceResponse(status="failed", message="No face detected", recognized=False)

# # #         if len(detections) > 1:
# # #             return AttendanceResponse(status="failed", message="Multiple faces detected", recognized=False)

# # #         bbox = detections[0]
# # #         aligned_face = align_face(frame, bbox)

# # #         # 2️⃣ Liveness
# # #         is_live = liveness_detector.predict(aligned_face)
# # #         if not is_live:
# # #             return AttendanceResponse(status="failed", message="Liveness check failed", recognized=False)

# # #         # 3️⃣ Recognition
# # #         embedding = face_recognizer.get_embedding(aligned_face)
# # #         user_id, distance = faiss_manager.search(embedding, k=1)

# # #         RECOGNITION_THRESHOLD = 0.6
# # #         confidence = float(1 - distance)

# # #         if distance > RECOGNITION_THRESHOLD:
# # #             return AttendanceResponse(
# # #                 status="failed",
# # #                 message="Face not recognized. Please register first.",
# # #                 recognized=False,
# # #                 liveness_passed=True
# # #             )

# # #         # 4️⃣ Fetch user safely
# # #         user = db_manager.get_user(db, user_id)
# # #         if user is None:
# # #             return AttendanceResponse(
# # #                 status="failed",
# # #                 message="Model recognized face but user not in database",
# # #                 recognized=False,
# # #                 liveness_passed=True
# # #             )

# # #         # 5️⃣ Check already marked
# # #         today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
# # #         existing = db_manager.get_attendance_by_user_and_date(db, user_id, today_start)

# # #         if existing:
# # #             return AttendanceResponse(
# # #                 status="already_marked",
# # #                 message=f"Attendance already marked for {user.name}",
# # #                 recognized=True,
# # #                 user_id=user_id,
# # #                 name=user.name,
# # #                 employee_id=user.employee_id,
# # #                 department=user.department,
# # #                 timestamp=existing.timestamp,
# # #                 confidence_score=confidence,
# # #                 liveness_passed=True
# # #             )

# # #         # 6️⃣ Mark attendance safely
# # #         record = db_manager.create_attendance(db, user_id, confidence)

# # #         if record is None:
# # #             return AttendanceResponse(status="failed", message="User not registered", recognized=False)

# # #         return AttendanceResponse(
# # #             status="success",
# # #             message=f"Attendance marked successfully for {user.name}",
# # #             recognized=True,
# # #             user_id=user_id,
# # #             name=user.name,
# # #             employee_id=user.employee_id,
# # #             department=user.department,
# # #             timestamp=record.timestamp,
# # #             confidence_score=confidence,
# # #             liveness_passed=True
# # #         )

# # #     except Exception as e:
# # #         return AttendanceResponse(status="failed", message=str(e), recognized=False)

# # """
# # Smart Attendance System - COMPLETE STABLE API
# # """

# # from fastapi import FastAPI, File, UploadFile, Form, Depends
# # from fastapi.middleware.cors import CORSMiddleware
# # from sqlalchemy.orm import Session
# # import numpy as np
# # import cv2
# # import torch
# # from datetime import datetime

# # from backend.models.face_detector import YOLOv9FaceDetector
# # from backend.models.face_recognizer import ArcFaceRecognizer
# # from backend.models.liveness_detector import LivenessDetector
# # from backend.database.db_manager import DatabaseManager, get_db
# # from backend.database.faiss_index import FAISSIndexManager
# # from backend.utils.face_alignment import align_face
# # from backend.utils.preprocessing import preprocess_frame
# # from backend.schemas import AttendanceResponse

# # app = FastAPI(title="Smart Attendance System")

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # face_detector=None
# # face_recognizer=None
# # liveness_detector=None
# # faiss_manager=None
# # db_manager=None


# # # ================= STARTUP =================
# # @app.on_event("startup")
# # async def startup_event():
# #     global face_detector, face_recognizer, liveness_detector, faiss_manager, db_manager

# #     device="cuda" if torch.cuda.is_available() else "cpu"

# #     face_detector=YOLOv9FaceDetector("weights/yolov9_face.pt",device=device)
# #     face_recognizer=ArcFaceRecognizer("weights/arcface_r100.pth",device=device)
# #     liveness_detector=LivenessDetector("weights/liveness_model.pth",device=device)
# #     faiss_manager=FAISSIndexManager(512,"data/faiss_index.bin")
# #     db_manager=DatabaseManager()

# #     print("✅ Backend Ready")


# # # ================= REGISTER =================
# # @app.post("/api/register")
# # async def register_user(
# #     name: str = Form(...),
# #     employee_id: str = Form(...),
# #     department: str = Form(...),
# #     file: UploadFile = File(...),
# #     db: Session = Depends(get_db)
# # ):

# #     contents = await file.read()
# #     frame=cv2.imdecode(np.frombuffer(contents,np.uint8),cv2.IMREAD_COLOR)

# #     detections=face_detector.detect(frame)
# #     if len(detections)==0:
# #         return {"status":"failed","message":"No face detected"}

# #     aligned=align_face(frame,detections[0])
# #     embedding=face_recognizer.get_embedding(aligned)

# #     user_id=db_manager.create_user(db,name,employee_id,department,embedding.tolist())
# #     faiss_manager.add_embedding(user_id,embedding)
# #     faiss_manager.save_index()

# #     return {"status":"success","user_id":user_id}


# # # ================= MARK ATTENDANCE =================
# # @app.post("/api/mark-attendance",response_model=AttendanceResponse)
# # async def mark_attendance(file:UploadFile=File(...),db:Session=Depends(get_db)):

# #     contents=await file.read()
# #     frame=cv2.imdecode(np.frombuffer(contents,np.uint8),cv2.IMREAD_COLOR)

# #     detections=face_detector.detect(frame)
# #     if len(detections)==0:
# #         return AttendanceResponse(status="failed",message="No face detected",recognized=False)

# #     aligned=align_face(frame,detections[0])

# #     if not liveness_detector.predict(aligned):
# #         return AttendanceResponse(status="failed",message="Liveness failed",recognized=False)

# #     embedding=face_recognizer.get_embedding(aligned)
# #     user_id,distance=faiss_manager.search(embedding,1)

# #     if distance>0.6:
# #         return AttendanceResponse(status="failed",message="Face not registered",recognized=False)

# #     user=db_manager.get_user(db,user_id)
# #     if not user:
# #         return AttendanceResponse(status="failed",message="User missing in DB",recognized=False)

# #     today=datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
# #     existing=db_manager.get_attendance_by_user_and_date(db,user_id,today)

# #     if existing:
# #         return AttendanceResponse(status="already_marked",message=f"Already marked for {user.name}",recognized=True)

# #     record=db_manager.create_attendance(db,user_id,1-distance)

# #     return AttendanceResponse(
# #         status="success",
# #         message=f"Welcome {user.name}",
# #         recognized=True,
# #         user_id=user_id,
# #         name=user.name,
# #         employee_id=user.employee_id,
# #         department=user.department,
# #         timestamp=record.timestamp,
# #         confidence_score=1-distance,
# #         liveness_passed=True
# #     )


# # # ================= DASHBOARD =================
# # @app.get("/api/stats/dashboard")
# # async def dashboard(db:Session=Depends(get_db)):
# #     users=db_manager.get_all_users(db)
# #     today=datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)

# #     present=0
# #     for u in users:
# #         if db_manager.get_attendance_by_user_and_date(db,u.id,today):
# #             present+=1

# #     return {
# #         "total_users":len(users),
# #         "present_today":present,
# #         "absent_today":len(users)-present
# #     }


# """
# Smart Attendance System - FINAL STABLE API
# Supports:
# • Multi-image registration
# • Face recognition attendance
# • Liveness detection
# • Dashboard stats
# """

# from fastapi import FastAPI, File, UploadFile, Form, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy.orm import Session
# from typing import List
# import numpy as np
# import cv2
# import torch
# from datetime import datetime

# from backend.models.face_detector import YOLOv9FaceDetector
# from backend.models.face_recognizer import ArcFaceRecognizer
# from backend.models.liveness_detector import LivenessDetector
# from backend.database.db_manager import DatabaseManager, get_db
# from backend.database.faiss_index import FAISSIndexManager
# from backend.utils.face_alignment import align_face
# from backend.utils.preprocessing import preprocess_frame
# from backend.schemas import AttendanceResponse

# # ---------------- APP ----------------
# app = FastAPI(title="Smart Attendance System")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# face_detector=None
# face_recognizer=None
# liveness_detector=None
# faiss_manager=None
# db_manager=None


# # ---------------- STARTUP ----------------
# @app.on_event("startup")
# async def startup_event():
#     global face_detector, face_recognizer, liveness_detector, faiss_manager, db_manager

#     device="cuda" if torch.cuda.is_available() else "cpu"

#     face_detector=YOLOv9FaceDetector("weights/yolov9_face.pt",device=device)
#     face_recognizer=ArcFaceRecognizer("weights/arcface_r100.pth",device=device)
#     liveness_detector=LivenessDetector("weights/liveness_model.pth",device=device)
#     faiss_manager=FAISSIndexManager(512,"data/faiss_index.bin")
#     db_manager=DatabaseManager()

#     print("✅ System Ready")


# # ---------------- REGISTER USER ----------------
# @app.post("/api/register")
# async def register_user(
#     name: str = Form(...),
#     employee_id: str = Form(...),
#     department: str = Form(...),
#     files: List[UploadFile] = File(...),
#     db: Session = Depends(get_db)
# ):
#     """
#     Register new user using multiple face images
#     """

#     if len(files) < 3:
#         return {"status":"failed","message":"Upload at least 3 images"}

#     embeddings=[]

#     for file in files:
#         contents=await file.read()
#         frame=cv2.imdecode(np.frombuffer(contents,np.uint8),cv2.IMREAD_COLOR)

#         if frame is None:
#             continue

#         detections=face_detector.detect(frame)
#         if len(detections)==0:
#             continue

#         aligned=align_face(frame,detections[0])

#         # liveness filter (skip fake images)
#         if not liveness_detector.predict(aligned):
#             continue

#         embedding=face_recognizer.get_embedding(aligned)
#         embeddings.append(embedding)

#     if len(embeddings)<3:
#         return {"status":"failed","message":"Face not clear in images"}

#     avg_embedding=np.mean(embeddings,axis=0)

#     user_id=db_manager.create_user(db,name,employee_id,department,avg_embedding.tolist())

#     faiss_manager.add_embedding(user_id,avg_embedding)
#     faiss_manager.save_index()

#     return {
#         "status":"success",
#         "user_id":user_id,
#         "images_used":len(embeddings)
#     }


# # ---------------- MARK ATTENDANCE ----------------
# @app.post("/api/mark-attendance",response_model=AttendanceResponse)
# async def mark_attendance(file:UploadFile=File(...),db:Session=Depends(get_db)):

#     contents=await file.read()
#     frame=cv2.imdecode(np.frombuffer(contents,np.uint8),cv2.IMREAD_COLOR)

#     if frame is None:
#         return AttendanceResponse(status="failed",message="Invalid image",recognized=False)

#     frame=preprocess_frame(frame)

#     detections=face_detector.detect(frame)

#     if len(detections)==0:
#         return AttendanceResponse(status="failed",message="No face detected",recognized=False)

#     if len(detections)>1:
#         return AttendanceResponse(status="failed",message="Multiple faces detected",recognized=False)

#     aligned=align_face(frame,detections[0])

#     if not liveness_detector.predict(aligned):
#         return AttendanceResponse(status="failed",message="Liveness check failed",recognized=False)

#     embedding=face_recognizer.get_embedding(aligned)
#     user_id,distance=faiss_manager.search(embedding,1)

#     if distance>0.6:
#         return AttendanceResponse(status="failed",message="Face not registered",recognized=False)

#     user=db_manager.get_user(db,user_id)

#     if not user:
#         return AttendanceResponse(status="failed",message="User missing in database",recognized=False)

#     today=datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
#     existing=db_manager.get_attendance_by_user_and_date(db,user_id,today)

#     if existing:
#         return AttendanceResponse(
#             status="already_marked",
#             message=f"Attendance already marked for {user.name}",
#             recognized=True,
#             user_id=user_id,
#             name=user.name,
#             employee_id=user.employee_id,
#             department=user.department,
#             timestamp=existing.timestamp,
#             confidence_score=1-distance,
#             liveness_passed=True
#         )

#     record=db_manager.create_attendance(db,user_id,1-distance)

#     return AttendanceResponse(
#         status="success",
#         message=f"Welcome {user.name}",
#         recognized=True,
#         user_id=user_id,
#         name=user.name,
#         employee_id=user.employee_id,
#         department=user.department,
#         timestamp=record.timestamp,
#         confidence_score=1-distance,
#         liveness_passed=True
#     )


# # ---------------- DASHBOARD ----------------
# @app.get("/api/stats/dashboard")
# async def dashboard(db:Session=Depends(get_db)):
#     users=db_manager.get_all_users(db)

#     today=datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
#     present=sum(1 for u in users if db_manager.get_attendance_by_user_and_date(db,u.id,today))

#     return {
#         "total_users":len(users),
#         "present_today":present,
#         "absent_today":len(users)-present
#     }

# """
# Database Manager for Smart Attendance System
# PostgreSQL + SQLAlchemy ORM
# """

# from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, relationship, Session
# from sqlalchemy.exc import IntegrityError
# from datetime import datetime
# from typing import List, Optional
# import os

# # Database configuration
# DATABASE_URL = os.getenv(
#     "DATABASE_URL",
#     "postgresql://attendance_user:attendance_pass@localhost:5432/attendance_db"
# )

# # Create engine
# engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# # Session factory
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Base class for models
# Base = declarative_base()


# # Database Models
# class User(Base):
#     """User model for registered persons"""
#     __tablename__ = "users"
    
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100), nullable=False)
#     employee_id = Column(String(50), unique=True, nullable=False, index=True)
#     department = Column(String(100), nullable=False)
#     face_embedding = Column(JSON, nullable=False)  # Store as JSON array
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relationship
#     attendance_records = relationship("Attendance", back_populates="user", cascade="all, delete-orphan")
    
#     def __repr__(self):
#         return f"<User(id={self.id}, name='{self.name}', employee_id='{self.employee_id}')>"


# class Attendance(Base):
#     """Attendance record model"""
#     __tablename__ = "attendance"
    
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
#     timestamp = Column(DateTime, default=datetime.utcnow, index=True)
#     confidence_score = Column(Float, nullable=False)
#     location = Column(String(200), nullable=True)
    
#     # Relationship
#     user = relationship("User", back_populates="attendance_records")
    
#     def __repr__(self):
#         return f"<Attendance(id={self.id}, user_id={self.user_id}, timestamp='{self.timestamp}')>"


# class AuditLog(Base):
#     """Audit log for system events"""
#     __tablename__ = "audit_logs"
    
#     id = Column(Integer, primary_key=True, index=True)
#     event_type = Column(String(50), nullable=False, index=True)
#     user_id = Column(Integer, nullable=True)
#     details = Column(JSON, nullable=True)
#     timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
#     def __repr__(self):
#         return f"<AuditLog(id={self.id}, event_type='{self.event_type}')>"


# # Database Manager Class
# class DatabaseManager:
#     """Manager class for database operations"""
    
#     def __init__(self):
#         """Initialize database manager"""
#         self.create_tables()
    
#     def create_tables(self):
#         """Create all tables"""
#         Base.metadata.create_all(bind=engine)
#         print("✅ Database tables created successfully")
    
#     def drop_tables(self):
#         """Drop all tables (use with caution!)"""
#         Base.metadata.drop_all(bind=engine)
#         print("⚠️  All tables dropped")
    
#     # User operations
#     def create_user(
#         self,
#         db: Session,
#         name: str,
#         employee_id: str,
#         department: str,
#         face_embedding: list
#     ) -> int:

#         employee_id = employee_id.lower().strip()

#     # 🔎 Check existing user
#         existing_user = db.query(User).filter(User.employee_id == employee_id).first()

#     # ---------------- UPDATE CASE ----------------
#         if existing_user:
#             existing_user.name = name
#             existing_user.department = department
#             existing_user.face_embedding = face_embedding
#             existing_user.updated_at = datetime.utcnow()

#             db.commit()
#             db.refresh(existing_user)

#             self.log_event(
#                 db,
#                 "user_re_registered",
#                 existing_user.id,
#                 {"employee_id": employee_id}
#             )

#             return existing_user.id

#     # ---------------- NEW USER CASE ----------------
#         new_user = User(
#             name=name,
#             employee_id=employee_id,
#             department=department,
#             face_embedding=face_embedding
#         )

#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)

#         self.log_event(
#             db,
#             "user_created",
#             new_user.id,
#             {"employee_id": employee_id}
#         )

#         return new_user.id
    
#     def get_user(self, db: Session, user_id: int) -> Optional[User]:
#         """Get user by ID"""
#         return db.query(User).filter(User.id == user_id).first()
    
#     def get_user_by_employee_id(self, db: Session, employee_id: str) -> Optional[User]:
#         """Get user by employee ID"""
#         return db.query(User).filter(User.employee_id == employee_id).first()
    
#     def get_all_users(self, db: Session) -> List[User]:
#         """Get all users"""
#         return db.query(User).all()
    
#     def update_user(
#         self,
#         db: Session,
#         user_id: int,
#         **kwargs
#     ) -> Optional[User]:
#         """Update user information"""
#         user = self.get_user(db, user_id)
#         if user:
#             for key, value in kwargs.items():
#                 if hasattr(user, key):
#                     setattr(user, key, value)
#             user.updated_at = datetime.utcnow()
#             db.commit()
#             db.refresh(user)
            
#             # Log event
#             self.log_event(db, "user_updated", user_id, kwargs)
        
#         return user
    
#     def delete_user(self, db: Session, user_id: int) -> bool:
#         """Delete a user"""
#         user = self.get_user(db, user_id)
#         if user:
#             db.delete(user)
#             db.commit()
            
#             # Log event
#             self.log_event(db, "user_deleted", user_id, {"name": user.name})
#             return True
#         return False
    
#     def count_total_users(self, db: Session) -> int:
#         """Count total registered users"""
#         return db.query(User).count()
    
#     # Attendance operations
#     def create_attendance(
#         self,
#         db: Session,
#         user_id: int,
#         confidence_score: float,
#         location: Optional[str] = None
#     ) -> Attendance:
#         """Create attendance record"""
#         attendance = Attendance(
#             user_id=user_id,
#             confidence_score=confidence_score,
#             location=location
#         )
#         db.add(attendance)
#         db.commit()
#         db.refresh(attendance)
        
#         # Log event
#         self.log_event(db, "attendance_marked", user_id, {"confidence": confidence_score})
        
#         return attendance
    
#     def get_attendance_by_id(self, db: Session, attendance_id: int) -> Optional[Attendance]:
#         """Get attendance record by ID"""
#         return db.query(Attendance).filter(Attendance.id == attendance_id).first()
    
#     def get_attendance_by_user_and_date(
#         self,
#         db: Session,
#         user_id: int,
#         date: datetime
#     ) -> Optional[Attendance]:
#         """Get attendance record for a user on a specific date"""
#         next_day = datetime(date.year, date.month, date.day, 23, 59, 59)
#         return db.query(Attendance).filter(
#             Attendance.user_id == user_id,
#             Attendance.timestamp >= date,
#             Attendance.timestamp <= next_day
#         ).first()
    
#     def get_user_attendance(
#         self,
#         db: Session,
#         user_id: int,
#         start_date: datetime,
#         end_date: datetime
#     ) -> List[Attendance]:
#         """Get attendance records for a user in date range"""
#         return db.query(Attendance).filter(
#             Attendance.user_id == user_id,
#             Attendance.timestamp >= start_date,
#             Attendance.timestamp <= end_date
#         ).order_by(Attendance.timestamp.desc()).all()
    
#     def get_attendance_by_date_range(
#         self,
#         db: Session,
#         start_date: datetime,
#         end_date: datetime
#     ) -> List[Attendance]:
#         """Get all attendance records in date range"""
#         return db.query(Attendance).filter(
#             Attendance.timestamp >= start_date,
#             Attendance.timestamp <= end_date
#         ).order_by(Attendance.timestamp.desc()).all()
    
#     def delete_attendance(self, db: Session, attendance_id: int) -> bool:
#         """Delete attendance record"""
#         attendance = self.get_attendance_by_id(db, attendance_id)
#         if attendance:
#             db.delete(attendance)
#             db.commit()
            
#             # Log event
#             self.log_event(db, "attendance_deleted", attendance.user_id, {"id": attendance_id})
#             return True
#         return False
    
#     # Audit log operations
#     def log_event(
#         self,
#         db: Session,
#         event_type: str,
#         user_id: Optional[int] = None,
#         details: Optional[dict] = None
#     ):
#         """Log system event"""
#         log = AuditLog(
#             event_type=event_type,
#             user_id=user_id,
#             details=details
#         )
#         db.add(log)
#         db.commit()
    
#     def get_audit_logs(
#         self,
#         db: Session,
#         start_date: Optional[datetime] = None,
#         end_date: Optional[datetime] = None,
#         event_type: Optional[str] = None,
#         limit: int = 100
#     ) -> List[AuditLog]:
#         """Get audit logs with filters"""
#         query = db.query(AuditLog)
        
#         if start_date:
#             query = query.filter(AuditLog.timestamp >= start_date)
#         if end_date:
#             query = query.filter(AuditLog.timestamp <= end_date)
#         if event_type:
#             query = query.filter(AuditLog.event_type == event_type)
        
#         return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()


# # Dependency for FastAPI
# def get_db():
#     """Get database session"""
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# # Initialize database
# if __name__ == "__main__":
#     print("Initializing database...")
#     db_manager = DatabaseManager()
#     print("✅ Database initialized successfully!")
    
#     # Example usage
#     db = SessionLocal()
    
#     try:
#         # Create test user
#         user_id = db_manager.create_user(
#             db=db,
#             name="John Doe",
#             employee_id="EMP001",
#             department="Engineering",
#             face_embedding=[0.1] * 512  # Dummy embedding
#         )
#         print(f"Created user with ID: {user_id}")
        
#         # Fetch user
#         user = db_manager.get_user(db, user_id)
#         print(f"Fetched user: {user}")
        
#         # Create attendance
#         attendance = db_manager.create_attendance(
#             db=db,
#             user_id=user_id,
#             confidence_score=0.95
#         )
#         print(f"Created attendance record: {attendance}")
        
#     finally:
#         db.close()

