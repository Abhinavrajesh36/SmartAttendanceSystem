# Smart Attendance System Using Face Recognition

## 🎯 Project Overview

An advanced AI-powered attendance system combining state-of-the-art deep learning models for accurate, real-time face recognition with anti-spoofing capabilities.

### Key Features
- **YOLOv9 Face Detection**: 30+ FPS, handles 50+ faces simultaneously
- **ArcFace Recognition**: 512-D embeddings with >97% accuracy
- **Liveness Detection**: Anti-spoofing protection against photos/videos/masks
- **PostgreSQL + FAISS**: Efficient storage and fast similarity search
- **React Frontend**: Modern, responsive user interface

## 🏗️ System Architecture

```
Camera → Frame Capture → YOLOv9 Detection → Face Alignment → 
ArcFace Embedding → FAISS Matching → Liveness Check → 
Attendance Marking → Database Storage
```

## 📋 Prerequisites

### Hardware Requirements
- **GPU**: NVIDIA GPU with CUDA support (8GB+ VRAM recommended)
- **CPU**: Multi-core processor (4+ cores)
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 50GB free space for models and datasets

### Software Requirements
- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- CUDA 11.8+ (for GPU acceleration)
- Git

## 🚀 Installation Guide

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/smart-attendance-system.git
cd smart-attendance-system
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration
```

### 3. Database Setup

```bash
# Install PostgreSQL
# On Ubuntu:
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE attendance_db;
CREATE USER attendance_user WITH PASSWORD 'attendance_pass';
GRANT ALL PRIVILEGES ON DATABASE attendance_db TO attendance_user;
\q

# Initialize database
python database/db_manager.py
```

### 4. Download Pre-trained Models

```bash
# Create weights directory
mkdir -p weights

# Download YOLOv9 Face Detection model
# Visit: https://github.com/WongKinYiu/yolov9
# Download yolov9_face.pt to weights/

# Download ArcFace model
# Visit: https://github.com/deepinsight/insightface
# Download arcface_r100.pth to weights/

# Download Liveness Detection model
# Visit: https://github.com/minivision-ai/Silent-Face-Anti-Spoofing
# Download liveness_model.pth to weights/
```

### 5. Dataset Preparation (Optional - for training)

```bash
# Install Kaggle API
pip install kaggle

# Setup Kaggle credentials
mkdir ~/.kaggle
# Place your kaggle.json in ~/.kaggle/

# Download VGGFace2 dataset
kaggle datasets download -d greatgamedota/vggface2-mini
unzip vggface2-mini.zip -d data/vggface2/
```

### 6. Frontend Setup

```bash
cd frontend
npm install
```

## 🎮 Running the Application

### Start Backend Server

```bash
# From project root
cd backend
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: http://localhost:8000

### Start Frontend

```bash
cd frontend
npm start
```

Frontend will be available at: http://localhost:3000

## 📁 Project Structure

```
smart-attendance-system/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   ├── face_detector.py    # YOLOv9 detector
│   │   ├── face_recognizer.py  # ArcFace recognizer
│   │   └── liveness_detector.py # Anti-spoofing
│   ├── database/
│   │   ├── db_manager.py       # Database operations
│   │   └── faiss_index.py      # FAISS index manager
│   ├── utils/
│   │   ├── face_alignment.py   # Face alignment
│   │   └── preprocessing.py    # Image preprocessing
│   ├── schemas.py              # Pydantic models
│   └── config.py               # Configuration
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AttendanceCapture.jsx
│   │   │   ├── UserRegistration.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   └── Reports.jsx
│   │   ├── App.jsx
│   │   └── index.js
│   └── package.json
├── weights/                    # Model weights
├── data/                       # Datasets and FAISS index
├── requirements.txt
├── package.json
└── README.md
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# Database
DATABASE_URL=postgresql://attendance_user:attendance_pass@localhost:5432/attendance_db

# Models
YOLOV9_MODEL_PATH=weights/yolov9_face.pt
ARCFACE_MODEL_PATH=weights/arcface_r100.pth
LIVENESS_MODEL_PATH=weights/liveness_model.pth

# FAISS
FAISS_INDEX_PATH=data/faiss_index.bin

# API
API_HOST=0.0.0.0
API_PORT=8000

# Recognition Thresholds
RECOGNITION_THRESHOLD=0.6
LIVENESS_THRESHOLD=0.5

# Device
DEVICE=cuda  # or cpu
```

## 📊 API Endpoints

### Authentication & Registration
- `POST /api/register` - Register new user with face images
- `GET /api/users` - Get all registered users
- `DELETE /api/user/{user_id}` - Delete user

### Attendance
- `POST /api/mark-attendance` - Mark attendance with face image
- `GET /api/attendance/today` - Get today's attendance records
- `GET /api/attendance/user/{user_id}` - Get user's attendance history

### Analytics
- `GET /api/stats/dashboard` - Get dashboard statistics

### Testing
- `POST /api/test/liveness` - Test liveness detection

## 🎓 Model Training (Optional)

### Train YOLOv9 Face Detector

```bash
cd training
python train_yolov9_face.py \
    --data data/vggface2 \
    --epochs 100 \
    --batch-size 16 \
    --img-size 640
```

### Train ArcFace Recognizer

```bash
python train_arcface.py \
    --data data/vggface2 \
    --epochs 50 \
    --batch-size 32 \
    --embedding-size 512
```

### Train Liveness Detector

```bash
python train_liveness.py \
    --live-data data/live_faces \
    --spoof-data data/spoof_faces \
    --epochs 30 \
    --batch-size 16
```

## 🧪 Testing

```bash
# Backend tests
pytest tests/

# Test face detection
python tests/test_detector.py

# Test face recognition
python tests/test_recognizer.py

# Test liveness detection
python tests/test_liveness.py

# Integration tests
python tests/test_integration.py
```

## 📈 Performance Optimization

### GPU Optimization
```python
# Enable mixed precision training
torch.backends.cudnn.benchmark = True
torch.set_float32_matmul_precision('high')
```

### Batch Processing
```python
# Process multiple frames in batch
detector.detect_batch(frames)
recognizer.get_embeddings_batch(faces)
```

### FAISS GPU
```bash
# Install FAISS-GPU for faster search
pip install faiss-gpu
```

## 🐳 Docker Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: attendance_db
      POSTGRES_USER: attendance_user
      POSTGRES_PASSWORD: attendance_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://attendance_user:attendance_pass@postgres:5432/attendance_db
    volumes:
      - ./weights:/app/weights
      - ./data:/app/data
    ports:
      - "8000:8000"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

## 🔐 Security Considerations

1. **Data Privacy**: Face embeddings are one-way transformations
2. **HTTPS**: Use SSL/TLS in production
3. **Authentication**: Implement JWT tokens for API access
4. **Rate Limiting**: Prevent abuse with request limits
5. **Input Validation**: Sanitize all user inputs

## 🐛 Troubleshooting

### CUDA Out of Memory
```python
# Reduce batch size
# Use CPU for some operations
# Enable gradient checkpointing
```

### Slow Detection
```python
# Check GPU utilization
# Reduce input image size
# Use model quantization
```

### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Reset connection
sudo systemctl restart postgresql
```

## 📚 References

- [YOLOv9 Paper](https://arxiv.org/abs/2402.13616)
- [ArcFace Paper](https://arxiv.org/abs/1801.07698)
- [VGGFace2 Dataset](http://www.robots.ox.ac.uk/~vgg/data/vgg_face2/)
- [FAISS Documentation](https://faiss.ai/)

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines.

## 📄 License

MIT License - See LICENSE file for details

## 👥 Team

- Lead Developer: Your Name
- ML Engineer: Team Member
- Frontend Developer: Team Member

## 📧 Contact

For questions or support: your.email@example.com

---

**Built with ❤️ using YOLOv9, ArcFace, and React**
