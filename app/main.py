# app/main.py
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, profiles, projects, matches, admin  
from app.database import engine, Base

app = FastAPI(title='MedMatch API', version='1.0')

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Register Routers
app.include_router(auth.router, prefix='/api/auth', tags=['Auth'])
app.include_router(profiles.router, prefix='/api/profiles', tags=['Profiles'])
app.include_router(projects.router, prefix='/api/projects', tags=['Projects'])
app.include_router(matches.router, prefix='/api/matches', tags=['Matches'])
app.include_router(admin.router,    prefix='/api/admin',    tags=['Admin']) 

@app.get('/')
def health_check():
    return {'status': 'MedMatch API is running'}