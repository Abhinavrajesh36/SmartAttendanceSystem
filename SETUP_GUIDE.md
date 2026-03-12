# Smart Attendance System - Complete Setup Guide

## 📦 Project Structure

```
smart-attendance-system/
│
├── backend/                        # Backend API (Python/FastAPI)
│   ├── main.py                     # Main FastAPI application
│   ├── config.py                   # Configuration settings
│   ├── schemas.py                  # Pydantic models
│   │
│   ├── models/                     # AI Models
│   │   ├── __init__.py
│   │   ├── face_detector.py        # YOLOv9 face detector
│   │   ├── face_recognizer.py      # ArcFace recognizer
│   │   └── liveness_detector.py    # Anti-spoofing
│   │
│   ├── database/                   # Database layer
│   │   ├── __init__.py
│   │   ├── db_manager.py           # PostgreSQL manager
│   │   └── faiss_index.py          # FAISS vector search
│   │
│   ├── utils/                      # Utilities
│   │   ├── __init__.py
│   │   ├── face_alignment.py       # Face alignment
│   │   └── preprocessing.py        # Image preprocessing
│   │
│   └── tests/                      # Unit tests
│       ├── __init__.py
│       ├── test_detector.py
│       ├── test_recognizer.py
│       └── test_liveness.py
│
├── frontend/                       # React Frontend
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   │
│   ├── src/
│   │   ├── components/
│   │   │   ├── AttendanceCapture.jsx    # Main attendance page
│   │   │   ├── UserRegistration.jsx     # User registration
│   │   │   ├── Dashboard.jsx            # Admin dashboard
│   │   │   ├── Reports.jsx              # Reports page
│   │   │   └── UserList.jsx             # User management
│   │   │
│   │   ├── App.jsx                      # Main app component
│   │   ├── index.js                     # Entry point
│   │   └── index.css                    # Tailwind CSS
│   │
│   ├── package.json
│   └── tailwind.config.js
│
├── training/                       # Model training scripts
│   ├── train_yolov9.py            # Train YOLOv9
│   ├── train_arcface.py           # Train ArcFace
│   └── train_liveness.py          # Train liveness detector
│
├── weights/                        # Pre-trained model weights
│   ├── yolov9_face.pt
│   ├── arcface_r100.pth
│   └── liveness_model.pth
│
├── data/                           # Data directory
│   ├── vggface2/                  # Training dataset
│   ├── faiss_index.bin            # FAISS index
│   └── uploads/                   # Uploaded images
│
├── docker/                         # Docker files
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
│
├── docs/                           # Documentation
│   ├── API.md                     # API documentation
│   ├── DEPLOYMENT.md              # Deployment guide
│   └── TROUBLESHOOTING.md         # Common issues
│
├── .env.example                    # Environment variables template
├── .gitignore
├── docker-compose.yml
├── requirements.txt                # Python dependencies
├── package.json                    # Node.js dependencies
└── README.md                       # This file
```

## 🛠️ Step-by-Step Installation

### Step 1: System Requirements

**Hardware:**
- GPU: NVIDIA GPU with 8GB+ VRAM (RTX 3060 or better)
- CPU: 4+ cores
- RAM: 16GB minimum, 32GB recommended
- Storage: 50GB free space

**Software:**
- Ubuntu 20.04+ or Windows 10/11
- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- CUDA 11.8+
- Docker (optional)

### Step 2: Install CUDA and cuDNN

```bash
# Ubuntu
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
sudo sh cuda_11.8.0_520.61.05_linux.run

# Add to ~/.bashrc
export PATH=/usr/local/cuda-11.8/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64:$LD_LIBRARY_PATH

# Verify installation
nvcc --version
nvidia-smi
```

### Step 3: Install PostgreSQL

```bash
# Ubuntu
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE attendance_db;
CREATE USER attendance_user WITH PASSWORD 'attendance_pass';
GRANT ALL PRIVILEGES ON DATABASE attendance_db TO attendance_user;
ALTER DATABASE attendance_db OWNER TO attendance_user;
\q
```

### Step 4: Clone and Setup Backend

```bash
# Clone repository (or copy provided files)
mkdir smart-attendance-system
cd smart-attendance-system

# Create project structure
mkdir -p backend/{models,database,utils,tests}
mkdir -p frontend/src/components
mkdir -p weights data training docs

# Copy all provided files to respective directories

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install PyTorch with CUDA support
pip install torch==2.1.1 torchvision==0.16.1 --index-url https://download.pytorch.org/whl/cu118
```

### Step 5: Setup Environment Variables

Create `.env` file in project root:

```env
# Database
DATABASE_URL=postgresql://attendance_user:attendance_pass@localhost:5432/attendance_db

# Model Paths
YOLOV9_MODEL_PATH=weights/yolov9_face.pt
ARCFACE_MODEL_PATH=weights/arcface_r100.pth
LIVENESS_MODEL_PATH=weights/liveness_model.pth

# FAISS Index
FAISS_INDEX_PATH=data/faiss_index.bin

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Recognition Thresholds
RECOGNITION_THRESHOLD=0.6
LIVENESS_THRESHOLD=0.5

# Device Configuration
DEVICE=cuda  # Use 'cpu' if no GPU available

# Security
SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
```

### Step 6: Download Pre-trained Models

**Option A: Download from official sources**

```bash
# YOLOv9 Face Detection
cd weights
wget https://github.com/WongKinYiu/yolov9/releases/download/v0.1/yolov9-c.pt -O yolov9_face.pt

# ArcFace (you'll need to train or find pre-trained weights)
# Visit: https://github.com/deepinsight/insightface

# Liveness Detection (you'll need to train or find pre-trained weights)
# Visit: https://github.com/minivision-ai/Silent-Face-Anti-Spoofing
```

**Option B: Train your own models** (see Training section below)

### Step 7: Initialize Database

```bash
cd backend
python database/db_manager.py
```

### Step 8: Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Install additional packages
npm install react-webcam axios lucide-react react-router-dom recharts date-fns

# Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

Create `tailwind.config.js`:

```javascript
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Create `src/index.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Step 9: Create Frontend App Structure

Create `frontend/src/App.jsx`:

```jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import AttendanceCapture from './components/AttendanceCapture';
import UserRegistration from './components/UserRegistration';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <nav className="bg-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold text-indigo-600">
                Smart Attendance System
              </h1>
              <div className="space-x-4">
                <Link to="/" className="text-gray-700 hover:text-indigo-600">
                  Attendance
                </Link>
                <Link to="/register" className="text-gray-700 hover:text-indigo-600">
                  Register
                </Link>
              </div>
            </div>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<AttendanceCapture />} />
          <Route path="/register" element={<UserRegistration />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
```

## 🚀 Running the Application

### Start Backend

```bash
# Terminal 1: Start backend
cd backend
source ../venv/bin/activate
python main.py

# Or use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be running at: **http://localhost:8000**
API documentation: **http://localhost:8000/docs**

### Start Frontend

```bash
# Terminal 2: Start frontend
cd frontend
npm start
```

Frontend will be running at: **http://localhost:3000**

## 📊 Using the System

### 1. Register Users

1. Navigate to **http://localhost:3000/register**
2. Fill in user details:
   - Name
   - Employee ID
   - Department
3. Upload 5-10 clear face images
4. Click "Register User"

### 2. Mark Attendance

1. Navigate to **http://localhost:3000**
2. Position face in front of camera
3. Click "Mark Attendance"
4. System will:
   - Detect face using YOLOv9
   - Verify liveness
   - Recognize face using ArcFace
   - Mark attendance in database

## 🎓 Training Models (Optional)

### Download VGGFace2 Dataset

```bash
# Install Kaggle CLI
pip install kaggle

# Setup Kaggle credentials
mkdir ~/.kaggle
# Download kaggle.json from Kaggle account
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Download dataset
kaggle datasets download -d greatgamedota/vggface2-mini
unzip vggface2-mini.zip -d data/vggface2/
```

### Train ArcFace Model

```bash
cd training
python train_arcface.py \
    --data ../data/vggface2/train \
    --val-data ../data/vggface2/val \
    --epochs 50 \
    --batch-size 32 \
    --embedding-size 512
```

## 🐳 Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Test specific module
pytest tests/test_detector.py -v

# Test with coverage
pytest tests/ --cov=models --cov-report=html
```

## 📈 Performance Monitoring

### Check GPU Usage

```bash
watch -n 1 nvidia-smi
```

### Backend Logs

```bash
tail -f backend/logs/app.log
```

### Database Queries

```bash
psql -U attendance_user -d attendance_db
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM attendance WHERE DATE(timestamp) = CURRENT_DATE;
```

## 🔒 Production Deployment Checklist

- [ ] Change all default passwords
- [ ] Enable HTTPS with SSL certificates
- [ ] Setup firewall rules
- [ ] Configure rate limiting
- [ ] Enable database backups
- [ ] Setup monitoring (Prometheus, Grafana)
- [ ] Configure logging (ELK stack)
- [ ] Enable CORS properly
- [ ] Use environment variables for secrets
- [ ] Setup CI/CD pipeline

## 📞 Support

For issues or questions, refer to:
- **Documentation**: `docs/` directory
- **API Docs**: http://localhost:8000/docs
- **GitHub Issues**: [Project Repository]

---

**Built with ❤️ using YOLOv9, ArcFace, and React**
