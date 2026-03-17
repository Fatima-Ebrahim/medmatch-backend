# MedMatch Backend

Mentor-Mentee Matching Platform for MedStar Health Research Institute

## Tech Stack
- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Sentence Transformers (AI Matching)

## Setup

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`
5. Create `.env` file from `.env.example`
6. Run migrations: `alembic upgrade head`
7. Start server: `uvicorn app.main:app --reload`

## API Documentation
http://localhost:8000/docs

## License
MIT