from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.match import Match
from app.models.mentor_profile import MentorProfile
from app.schemas.match import MatchOut
from app.core.dependencies import get_current_user
from app.services.matching import run_matching
from app.services.email import send_match_accepted_email

router = APIRouter()

@router.get('/mine', response_model=list[MatchOut])
def get_my_matches(current_user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    if current_user.role == 'mentee':
        return db.query(Match).filter(Match.mentee_id == current_user.id).all()
    elif current_user.role == 'mentor':
        return db.query(Match).filter(Match.mentor_id == current_user.id).all()
    elif current_user.role == 'investigator':
        from app.models.project import Project
        project_ids = [p.id for p in db.query(Project).filter(
            Project.investigator_id == current_user.id).all()]
        return db.query(Match).filter(Match.project_id.in_(project_ids)).all()
    return []

@router.post('/{match_id}/accept')
def accept_match(match_id: int,
                 current_user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail='Match not found')
    
    # Check this user is part of the match
    if current_user.id not in [match.mentee_id, match.mentor_id]:
        raise HTTPException(status_code=403, detail='Not your match')
    
    match.status = 'active'
    db.commit()
    
    # Check if mentor is now full → set availability = False
    if match.mentor_id:
        mentor_profile = db.query(MentorProfile).filter(
            MentorProfile.user_id == match.mentor_id).first()
        if mentor_profile:
            active_count = db.query(Match).filter(
                Match.mentor_id == match.mentor_id,
                Match.status == 'active').count()
            if active_count >= mentor_profile.max_mentees:
                mentor_profile.availability = False
                db.commit()
    
    send_match_accepted_email(match, db)
    return {'message': 'Match accepted'}

@router.post('/{match_id}/decline')
def decline_match(match_id: int,
                  current_user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail='Match not found')
    
    match.status = 'declined'
    db.commit()
    
    # Re-run matching to find the next best option
    run_matching(match.mentee_id, db, exclude_ids=[match.mentor_id])
    return {'message': 'Match declined. Re-matching in progress.'}