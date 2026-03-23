# 🩺 MedMatch Backend API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://github.com/YOUR_USERNAME/medmatch-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/medmatch-backend/actions)

AI-powered mentor-mentee matching platform for MedStar Health Research Institute. Matches researchers based on semantic similarity using sentence embeddings.

## 🚀 Features
- **JWT Authentication** (Role-based access control)
- **AI Matching** (Sentence Transformers + Cosine Similarity)
- **Automated Emails** (Resend.com integration)
- **Admin Dashboard** (User management, CSV import, Review queue)
- **Background Jobs** (Match expiry cron jobs)

## 🛠 Tech Stack
- **Backend:** Python 3.11, FastAPI
- **Database:** PostgreSQL 15+, SQLAlchemy 2.0
- **AI:** sentence-transformers, scikit-learn
- **Deployment:** Render.com, Docker
- **Testing:** pytest, httpx

## 📦 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL
- Docker (optional)

### Local Setup
```bash
# 1. Clone repo
git clone https://github.com/YOUR_USERNAME/medmatch-backend.git
cd medmatch-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your database URL and secrets

# 5. Run migrations
alembic upgrade head

# 6. Start server
uvicorn app.main:app --reload