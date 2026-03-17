import csv, io, json
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.mentor_profile import MentorProfile
from app.models.mentee_profile import MenteeProfile
from app.models.bulk_upload_job import BulkUploadJob
from app.core.security import hash_password
from app.services.embedding import get_embedding

REQUIRED_COLUMNS = {'email', 'full_name', 'role', 'password'}
VALID_ROLES = {'mentee', 'mentor', 'investigator'}

def process_csv(file_bytes: bytes, admin_id: int, db: Session) -> BulkUploadJob:
    job = BulkUploadJob(admin_id=admin_id)
    db.add(job)
    db.commit()
    db.refresh(job)
    
    reader = csv.DictReader(io.StringIO(file_bytes.decode('utf-8')))
    rows = list(reader)
    job.total_rows = len(rows)
    job.status = 'processing'
    db.commit()
    
    errors = []
    for i, row in enumerate(rows, start=2):  # row 1 is header
        missing = REQUIRED_COLUMNS - set(row.keys())
        if missing:
            errors.append({'row': i, 'reason': f'Missing columns: {missing}'})
            continue
        
        email = row['email'].strip().lower()
        role  = row['role'].strip().lower()
        
        if role not in VALID_ROLES:
            errors.append({'row': i, 'reason': f'Invalid role: {role}'})
            continue
        
        if db.query(User).filter(User.email == email).first():
            errors.append({'row': i, 'reason': f'Email already exists: {email}'})
            continue
        
        if len(row['password']) < 8:
            errors.append({'row': i, 'reason': 'Password too short (min 8 chars)'})
            continue
        
        user = User(email=email, full_name=row['full_name'].strip(),
                    password_hash=hash_password(row['password']), role=role)
        db.add(user)
        db.flush()  # get user.id without full commit
        
        if role == 'mentor':
            expertise = row.get('expertise_tags', '')
            bio = row.get('bio', '')
            emb = json.dumps(get_embedding(f'{expertise} {bio}')) if expertise or bio else None
            db.add(MentorProfile(user_id=user.id, expertise_tags=expertise, bio=bio, embedding=emb))
        elif role == 'mentee':
            skills = row.get('desired_skills', '')
            emb = json.dumps(get_embedding(skills)) if skills else None
            db.add(MenteeProfile(user_id=user.id, desired_skills=skills, embedding=emb))
        
        job.processed_rows += 1
    
    job.error_log = json.dumps(errors)
    job.status = 'done' if not errors or job.processed_rows > 0 else 'failed'
    db.commit()
    return job