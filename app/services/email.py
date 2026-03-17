import resend
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User
from app.models.match import Match

# Set API Key (Will fail gracefully if key is missing)
resend.api_key = settings.RESEND_API_KEY

def send_email(to: str, subject: str, html: str):
    """Low-level send. All other functions call this one."""
    if not settings.RESEND_API_KEY:
        print(f"[EMAIL MOCK] To: {to} | Subject: {subject}")
        return
    
    try:
        resend.Emails.send({
            'from':    'MedMatch <onboarding@resend.dev>', # Use verified domain in prod
            'to':      [to],
            'subject': subject,
            'html':    html,
        })
    except Exception as e:
        print(f'[EMAIL ERROR] Could not send to {to}: {e}')

def send_match_suggested_email(match: Match, db: Session):
    """Email sent when a new match is created (status = pending)."""
    mentee = db.query(User).filter(User.id == match.mentee_id).first()
    if match.mentor_id:
        other = db.query(User).filter(User.id == match.mentor_id).first()
        subject = 'MedMatch — A Mentee Has Been Matched to You'
        send_email(other.email, subject,
            f'<p>Hi {other.full_name},</p>'
            f'<p>A new mentee, <b>{mentee.full_name}</b>, has been matched to you '
            f'with a score of <b>{match.score}%</b>.</p>')
    
    send_email(mentee.email, 'MedMatch — Your Match Is Ready',
        f'<p>Hi {mentee.full_name},</p>'
        f'<p>We found a match for you! Log in to view your suggested mentor or project.</p>')

def send_match_accepted_email(match: Match, db: Session):
    """Email sent to both parties when status becomes active."""
    mentee = db.query(User).filter(User.id == match.mentee_id).first()
    send_email(mentee.email, 'MedMatch — Your Match is Confirmed!',
        f'<p>Hi {mentee.full_name}, your match has been confirmed. Good luck!</p>')
    if match.mentor_id:
        mentor = db.query(User).filter(User.id == match.mentor_id).first()
        send_email(mentor.email, 'MedMatch — Match Confirmed',
            f'<p>Hi {mentor.full_name}, your match with {mentee.full_name} is confirmed.</p>')