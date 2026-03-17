# app/tasks/expire_matches.py
from datetime import datetime
from app.database import SessionLocal
from app.models.match import Match
from app.services.matching import run_matching

def expire_old_matches():
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        # Find pending matches past their expiry date
        expired = db.query(Match).filter(
            Match.status == 'pending',
            Match.expires_at < now
        ).all()
        print(f'⏰ Found {len(expired)} expired matches.')
        
        for match in expired:
            match.status = 'expired'
            db.commit()
            # Re-match the mentee with next best option
            # Exclude the expired mentor/project
            exclude = []
            if match.mentor_id: exclude.append(match.mentor_id)
            if match.project_id: exclude.append(match.project_id)
            
            run_matching(match.mentee_id, db, exclude_ids=exclude)
            print(f'  → Match {match.id} expired. Re-matching mentee {match.mentee_id}.')
    finally:
        db.close()

if __name__ == '__main__':
    expire_old_matches()