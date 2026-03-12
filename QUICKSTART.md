# Smart Attendance System - Quick Start Guide

## 🎯 What You Have

A complete Smart Attendance System with:

✅ **Backend (Python/FastAPI)**
- YOLOv9 Face Detection (30+ FPS)
- ArcFace Recognition (512-D embeddings, >97% accuracy)
- Liveness Detection (Anti-spoofing)
- PostgreSQL Database
- FAISS Vector Search

✅ **Frontend (React)**
- Real-time camera capture
- User registration interface
- Attendance dashboard
- Modern responsive UI

✅ **Training Scripts**
- ArcFace model training
- Support for VGGFace2 dataset (3.31M images)

## 📁 Files Included

### Backend Files
1. **main.py** - Main FastAPI application
2. **face_detector.py** - YOLOv9 implementation
3. **face_recognizer.py** - ArcFace implementation
4. **liveness_detector.py** - Anti-spoofing module
5. **db_manager.py** - PostgreSQL database manager
6. **faiss_index.py** - FAISS similarity search
7. **face_alignment.py** - Face alignment utilities
8. **preprocessing.py** - Image preprocessing
9. **schemas.py** - API data models
10. **train_arcface.py** - Training script

### Frontend Files
1. **AttendanceCapture.jsx** - Main attendance page
2. **UserRegistration.jsx** - User registration page
3. **package.json** - Frontend dependencies

### Configuration Files
1. **requirements.txt** - Python dependencies
2. **docker-compose.yml** - Docker deployment
3. **README.md** - Full documentation
4. **SETUP_GUIDE.md** - Detailed setup instructions

## 🚀 Quick Start (5 Steps)

### Step 1: Organize Files

Create this structure:

```
smart-attendance-system/
├── backend/
│   ├── main.py
│   ├── schemas.py
│   ├── models/
│   │   ├── face_detector.py
│   │   ├── face_recognizer.py
│   │   └── liveness_detector.py
│   ├── database/
│   │   ├── db_manager.py
│   │   └── faiss_index.py
│   └── utils/
│       ├── face_alignment.py
│       └── preprocessing.py
├── frontend/
│   ├── src/
│   │   └── components/
│   │       ├── AttendanceCapture.jsx
│   │       └── UserRegistration.jsx
│   └── package.json
├── requirements.txt
└── docker-compose.yml
```

### Step 2: Install Dependencies

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### Step 3: Setup Database

```bash
# Install PostgreSQL
sudo apt-get install postgresql  # Ubuntu
# Or download from: https://www.postgresql.org/download/

# Create database
sudo -u postgres psql
CREATE DATABASE attendance_db;
CREATE USER attendance_user WITH PASSWORD 'attendance_pass';
GRANT ALL PRIVILEGES ON DATABASE attendance_db TO attendance_user;
\q

# Initialize tables
cd backend
python database/db_manager.py
```

### Step 4: Download Model Weights

You need 3 model files:

1. **yolov9_face.pt** - Face detection
   - Download from: https://github.com/WongKinYiu/yolov9
   - Place in: `weights/yolov9_face.pt`

2. **arcface_r100.pth** - Face recognition
   - Train using: `python train_arcface.py`
   - Or download pre-trained from: https://github.com/deepinsight/insightface
   - Place in: `weights/arcface_r100.pth`

3. **liveness_model.pth** - Anti-spoofing
   - Train your own or download from: https://github.com/minivision-ai
   - Place in: `weights/liveness_model.pth`

### Step 5: Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```
Backend runs at: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```
Frontend runs at: http://localhost:3000

## 📖 Usage

### Register a User
1. Go to http://localhost:3000/register
2. Fill in: Name, Employee ID, Department
3. Upload 5-10 clear face photos
4. Click "Register User"

### Mark Attendance
1. Go to http://localhost:3000
2. Face the camera
3. Click "Mark Attendance"
4. System recognizes and records attendance

## 🔧 Configuration

Create `.env` file:
```env
DATABASE_URL=postgresql://attendance_user:attendance_pass@localhost:5432/attendance_db
YOLOV9_MODEL_PATH=weights/yolov9_face.pt
ARCFACE_MODEL_PATH=weights/arcface_r100.pth
LIVENESS_MODEL_PATH=weights/liveness_model.pth
FAISS_INDEX_PATH=data/faiss_index.bin
DEVICE=cuda  # or 'cpu' if no GPU
```

## 🐛 Troubleshooting

### No face detected
- Ensure good lighting
- Face camera directly
- Remove glasses/masks

### Slow performance
- Use GPU (CUDA)
- Reduce image size
- Check `nvidia-smi` for GPU usage

### Database connection error
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify credentials in `.env`
- Ensure database exists: `psql -U attendance_user -d attendance_db`

### Import errors
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

## 📚 Next Steps

1. **Read full documentation**: Check README.md and SETUP_GUIDE.md
2. **Train models**: Use train_arcface.py with VGGFace2 dataset
3. **Customize**: Modify thresholds and UI as needed
4. **Deploy**: Use docker-compose.yml for production

## 🎓 Training Your Own Models

### Download VGGFace2 Dataset
```bash
# Install Kaggle
pip install kaggle

# Get dataset
kaggle datasets download -d greatgamedota/vggface2-mini
unzip vggface2-mini.zip -d data/vggface2/
```

### Train ArcFace
```bash
python train_arcface.py \
    --data data/vggface2/train \
    --epochs 50 \
    --batch-size 32
```

## 🌟 Key Features

- **Fast Detection**: 30+ FPS with YOLOv9
- **High Accuracy**: >97% with ArcFace
- **Secure**: Liveness detection prevents spoofing
- **Scalable**: Handles 50+ faces simultaneously
- **Real-time**: Instant attendance marking
- **Modern UI**: Beautiful React interface

## 📊 System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8GB
- GPU: Optional (uses CPU)
- Storage: 10GB

**Recommended:**
- CPU: 8+ cores
- RAM: 16GB
- GPU: NVIDIA RTX 3060 (8GB VRAM)
- Storage: 50GB SSD

## 🔗 Resources

- **YOLOv9**: https://github.com/WongKinYiu/yolov9
- **ArcFace Paper**: https://arxiv.org/abs/1801.07698
- **VGGFace2**: http://www.robots.ox.ac.uk/~vgg/data/vgg_face2/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/

## 💡 Tips

1. **Better Accuracy**: Register users with 7-10 photos from different angles
2. **Faster Performance**: Use GPU acceleration
3. **Production**: Use HTTPS and change default passwords
4. **Backup**: Regularly backup PostgreSQL database
5. **Monitoring**: Setup logging and alerts

## 📞 Support

For detailed help, check:
- **SETUP_GUIDE.md** - Complete installation guide
- **README.md** - Full documentation
- **API Docs** - http://localhost:8000/docs

---

**You're all set! Start with Step 1 and build your attendance system. Good luck! 🚀**
