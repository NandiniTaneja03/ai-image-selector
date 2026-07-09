# 🚀 AI Image Selector

An AI-powered image ranking system that uses OpenAI CLIP embeddings to rank candidate images based on a user's preferred images.

## ✨ Features

- 🖼 Upload liked/reference images
- 📤 Upload candidate images
- 🤖 AI-powered semantic similarity using CLIP
- 📊 Intelligent image ranking
- ⚡ FastAPI backend
- 🎨 Streamlit frontend
- 🔐 JWT Authentication
- 🗄 Database integration with SQLAlchemy

---

## 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| Backend | FastAPI |
| Frontend | Streamlit |
| AI Model | OpenAI CLIP (Transformers + PyTorch) |
| Database | SQLAlchemy |
| Authentication | JWT |
| Image Processing | Pillow, OpenCV |
| ML Libraries | PyTorch, Transformers, Scikit-learn |

---

# 📂 Project Structure

```
ai-image-selector/
│
├── app/
│   ├── main.py
│   ├── auth.py
│   ├── image_processor.py
│   ├── ranker.py
│   ├── models.py
│   └── schemas.py
│
├── frontend/
│   └── streamlit_app.py
│
├── uploads/
├── database/
├── models/
├── scripts/
├── docker/
│
├── requirements.txt
├── README.md
└── .env.example
```

---

# ⚙ Installation

## 1. Clone Repository

```bash
git clone https://github.com/your-username/ai-image-selector.git
cd ai-image-selector
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate

```bash
.\venv\Scripts\Activate.ps1
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶ Running the Project

### Start FastAPI Backend

```bash
python -m uvicorn app.main:app --reload
```

Backend URL

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

### Start Streamlit Frontend

Open another terminal.

```bash
python -m streamlit run frontend/streamlit_app.py
```

Frontend

```
http://localhost:8501
```

---

# 📌 Workflow

1. Register/Login
2. Upload Liked Images
3. Upload Candidate Images
4. Generate CLIP Embeddings
5. AI compares semantic similarity
6. Images ranked by similarity
7. View Top Ranked Results

---

# 📸 Demo

(Add screenshots here)

Backend

![Backend](screenshots/backend.png)

Frontend

![Frontend](screenshots/frontend.png)

Ranking

![Ranking](screenshots/ranking.png)

---

# Future Improvements

- User Dashboard
- Image History
- Better Recommendation Algorithm
- Batch Ranking
- Docker Deployment
- Cloud Storage (AWS S3)
- CI/CD Pipeline
- Admin Panel

---

# Author

**Nandini Taneja**

Computer Science Engineering Student


AI | Machine Learning | Full Stack Development

AI | Machine Learning | Full Stack Development

