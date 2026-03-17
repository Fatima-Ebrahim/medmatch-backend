from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.match import Match
from app.schemas.match import AdminReviewIn
from app.core.dependencies import require_admin
from app.services.csv_import import process_csv

router = APIRouter()

# ── User Management ─────────────────────────────────────────────
@router.get('/users')
def list_users(search: str = '', role: str = '',
               db: Session = Depends(get_db),
               admin: User = Depends(require_admin)):
    query = db.query(User)
    if search:
        query = query.filter(
            (User.full_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    if role:
        query = query.filter(User.role == role)
    return query.all()

@router.put('/users/{user_id}')
def update_user(user_id: int, body: dict,
                db: Session = Depends(get_db),
                admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    # Only allow updating safe fields
    allowed = {'full_name', 'email'}
    for field, value in body.items():
        if field in allowed:
            setattr(user, field, value)
    db.commit()
    return user

# ── Review Queue (70-84% Matches) ───────────────────────────────
@router.get('/review-queue')
def get_review_queue(db: Session = Depends(get_db),
                     admin: User = Depends(require_admin)):
    return db.query(Match).filter(Match.status == 'admin_review').all()

@router.post('/review-queue/{match_id}/confirm')
def confirm_borderline_match(match_id: int, body: AdminReviewIn,
                             db: Session = Depends(get_db),
                             admin: User = Depends(require_admin)):
    match = db.query(Match).filter(
        Match.id == match_id, Match.status == 'admin_review'
    ).first()
    if not match:
        raise HTTPException(status_code=404, detail='Match not found in review queue')
    
    match.admin_note = body.note
    match.status = 'pending' if body.confirm else 'declined'
    db.commit()
    return {'status': match.status}

# ── CSV Bulk Import ─────────────────────────────────────────────
@router.post('/bulk-import')
def bulk_import(file: UploadFile = File(...),
                db: Session = Depends(get_db),
                admin: User = Depends(require_admin)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail='Please upload a .csv file')
    
    contents = file.file.read()
    job = process_csv(contents, admin.id, db)
    return {
        'job_id': job.id,
        'total_rows': job.total_rows,
        'processed_rows': job.processed_rows,
        'errors': job.error_log,
        'status': job.status
    }
    
@router.post('/matches/{match_id}/assign-mentor')
def assign_mentor_to_match(match_id: int, mentor_id: int,
                           db: Session = Depends(get_db),
                           admin: User = Depends(require_admin)):
    """Assign a mentor to an existing project match."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail='Match not found')
    if not match.project_id:
        raise HTTPException(status_code=400, detail='This match is not for a project')
    
    # Assign the mentor
    match.mentor_id = mentor_id
    db.commit()
    return {'message': 'Mentor assigned to project match'}