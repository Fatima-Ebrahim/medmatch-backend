import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.mentee_profile import MenteeProfile
from app.models.mentor_profile import MentorProfile
from app.models.project import Project  # Required even if Router is Week 4
from app.models.match import Match
from app.services.embedding import match_score
from app.services.email import send_match_suggested_email

# Thresholds from MedMatch v2.2 Section 3.4
AUTO_THRESHOLD   = 85.0  # score >= this: auto-match
REVIEW_THRESHOLD = 70.0  # score >= this: admin review

# def run_matching(mentee_id: int, db: Session, exclude_ids: list = None):
#     """Find best mentor OR project for a given mentee. Called on profile save."""
#     exclude_ids = exclude_ids or []
#     mentee = db.query(MenteeProfile).filter(MenteeProfile.user_id == mentee_id).first()
    
#     if not mentee or not mentee.embedding:
#         return None
    
#     mentee_emb = json.loads(mentee.embedding)
#     candidates = []  # list of (score, mentor_id_or_None, project_id_or_None)
    
#     # Score all available mentors
#     for mentor in db.query(MentorProfile).filter(MentorProfile.availability == True).all():
#         if mentor.user_id in exclude_ids or not mentor.embedding:
#             continue
#         score = match_score(mentee_emb, json.loads(mentor.embedding))
#         candidates.append((score, mentor.user_id, None))
    
#     # Score all open projects
#     for project in db.query(Project).filter(Project.status == 'open').all():
#         if project.id in exclude_ids or not project.embedding:
#             continue
#         score = match_score(mentee_emb, json.loads(project.embedding))
#         candidates.append((score, None, project.id))
    
#     if not candidates:
#         return None
    
#     candidates.sort(key=lambda x: x[0], reverse=True)
#     best_score, best_mentor_id, best_project_id = candidates[0]
    
#     if best_score >= AUTO_THRESHOLD:
#         status = 'pending'
#     elif best_score >= REVIEW_THRESHOLD:
#         status = 'admin_review'
#     else:
#         return None  # no good match
def run_matching(mentee_id: int, db: Session, exclude_ids: list = None):
    print(f"🔍 [MATCHING] Starting matching for mentee_id={mentee_id}")
    
    exclude_ids = exclude_ids or []
    mentee = db.query(MenteeProfile).filter(MenteeProfile.user_id == mentee_id).first()
    
    if not mentee:
        print(f"❌ [MATCHING] No mentee profile found for user {mentee_id}")
        return None
    
    if not mentee.embedding:
        print(f"❌ [MATCHING] No embedding for mentee {mentee_id}")
        return None
    
    print(f"✅ [MATCHING] Mentee embedding found: {len(json.loads(mentee.embedding))} dimensions")
    
    mentors = db.query(MentorProfile).filter(MentorProfile.availability == True).all()
    print(f"📋 [MATCHING] Found {len(mentors)} available mentors")
    
    candidates = []
    for mentor in mentors:
        if not mentor.embedding:
            print(f"⚠️ [MATCHING] Mentor {mentor.user_id} has no embedding")
            continue
        score = match_score(json.loads(mentee.embedding), json.loads(mentor.embedding))
        print(f"🎯 [MATCHING] Mentor {mentor.user_id} score: {score}%")
        candidates.append((score, mentor.user_id, None))
    
    if not candidates:
        print(f"❌ [MATCHING] No candidates found")
        return None
    
    candidates.sort(key=lambda x: x[0], reverse=True)
    best_score, best_mentor_id, best_project_id = candidates[0]
    print(f"🏆 [MATCHING] Best match: mentor_id={best_mentor_id}, score={best_score}%")
    
    if best_score >= 85:
        status = 'pending'
        print(f"✅ [MATCHING] Auto-match created (score >= 85%)")
    elif best_score >= 70:
        status = 'admin_review'
        print(f"⚠️ [MATCHING] Admin review required (score 70-84%)")
    else:
        print(f"❌ [MATCHING] Score too low ({best_score}%), no match created")
        return None
    
    match = Match(
        mentee_id=mentee_id,
        mentor_id=best_mentor_id,
        project_id=best_project_id,
        score=best_score,
        status=status,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    
    if status == 'pending':
        send_match_suggested_email(match, db)
    
    return match

def run_project_matching(project_id: int, db: Session):
    """When a project is published, find all mentees who could match it."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or not project.embedding:
        return
    
    project_emb = json.loads(project.embedding)
    for mentee in db.query(MenteeProfile).filter(MenteeProfile.embedding != None).all():
        score = match_score(json.loads(mentee.embedding), project_emb)
        if score >= REVIEW_THRESHOLD:
            status = 'pending' if score >= AUTO_THRESHOLD else 'admin_review'
            match = Match(
                mentee_id=mentee.user_id,
                project_id=project_id,
                score=score, status=status,
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            db.add(match)
    db.commit()