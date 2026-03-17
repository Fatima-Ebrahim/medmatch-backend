from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import json, shutil, os
from app.database import get_db
from app.models.user import User
from app.models.mentor_profile import MentorProfile
from app.models.mentee_profile import MenteeProfile
from app.models.investigator_profile import InvestigatorProfile
from app.schemas.profile import (MentorProfileUpdate, MentorProfileOut, 
                                   MenteeProfileUpdate, MenteeProfileOut, 
                                   InvestigatorProfileUpdate)
from app.core.dependencies import get_current_user
from app.services.embedding import get_embedding
from app.services.matching import run_matching

router = APIRouter()

# ── GET my profile ──────────────────────────────────────────────
@router.get('/me')
def get_my_profile(current_user: User = Depends(get_current_user), 
                   db: Session = Depends(get_db)):
    if current_user.role == 'mentor':
        profile = db.query(MentorProfile).filter(MentorProfile.user_id == current_user.id).first()
    elif current_user.role == 'mentee':
        profile = db.query(MenteeProfile).filter(MenteeProfile.user_id == current_user.id).first()
    elif current_user.role == 'investigator':
        profile = db.query(InvestigatorProfile).filter(InvestigatorProfile.user_id == current_user.id).first()
    else:
        raise HTTPException(status_code=400, detail='Admins do not have profiles')
    return profile

# ── UPDATE mentor profile ────────────────────────────────────────
@router.put('/me/mentor')
def update_mentor_profile(body: MentorProfileUpdate, 
                          current_user: User = Depends(get_current_user), 
                          db: Session = Depends(get_db)):
    if current_user.role != 'mentor':
        raise HTTPException(status_code=403, detail='Only mentors can use this endpoint')
    
    profile = db.query(MentorProfile).filter(MentorProfile.user_id == current_user.id).first()
    if not profile:
        profile = MentorProfile(user_id=current_user.id)
        db.add(profile)
    
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(profile, field, value)
    
    # Re-generate embedding
    text = f"{profile.expertise_tags or ''} {profile.bio or ''}"
    profile.embedding = json.dumps(get_embedding(text))
    
    db.commit()
    db.refresh(profile)
    return profile

# ── UPDATE mentee profile (triggers re-matching) ─────────────────
@router.put('/me/mentee')
def update_mentee_profile(body: MenteeProfileUpdate, 
                          current_user: User = Depends(get_current_user), 
                          db: Session = Depends(get_db)):
    if current_user.role != 'mentee':
        raise HTTPException(status_code=403, detail='Only mentees can use this endpoint')
    
    profile = db.query(MenteeProfile).filter(MenteeProfile.user_id == current_user.id).first()
    if not profile:
        profile = MenteeProfile(user_id=current_user.id)
        db.add(profile)
    
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(profile, field, value)
    
    # Build text for embedding
    text = ' '.join(filter(None, [
        profile.research_interests,
        profile.goals,
        profile.desired_skills
    ]))
    profile.embedding = json.dumps(get_embedding(text))
    
    db.commit()
    db.refresh(profile)
    
    # Run matching (Stubbed for Week 2, fully implemented in Week 3)
    run_matching(current_user.id, db)
    
    return profile

@router.post('/me/cv')
def upload_cv(file: UploadFile = File(...),
              current_user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    if current_user.role != 'mentee':
        raise HTTPException(status_code=403, detail='Only mentees can upload a CV')
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail='Only PDF files are accepted')
    
    os.makedirs('uploads/cvs', exist_ok=True)
    path = f'uploads/cvs/mentee_{current_user.id}.pdf'
    with open(path, 'wb') as f:
        shutil.copyfileobj(file.file, f)
    
    profile = db.query(MenteeProfile).filter(MenteeProfile.user_id == current_user.id).first()
    if profile:
        profile.cv_file = path
        db.commit()
    return {'cv_file': path}