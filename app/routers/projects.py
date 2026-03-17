from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.core.dependencies import get_current_user
from app.services.embedding import get_embedding
from app.services.matching import run_project_matching

router = APIRouter()

@router.get('/', response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    """List all published projects."""
    return db.query(Project).filter(Project.status == 'open').all()

@router.post('/', response_model=ProjectOut, status_code=201)
def create_project(body: ProjectCreate,
                   current_user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    """Create a new project (draft). Investigators only."""
    if current_user.role != 'investigator':
        raise HTTPException(status_code=403, detail='Investigators only')
    
    project = Project(**body.model_dump(), investigator_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.put('/{project_id}', response_model=ProjectOut)
def update_project(project_id: int, body: ProjectUpdate,
                   current_user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    """Edit a project. Owner only."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail='Project not found')
    if project.investigator_id != current_user.id:
        raise HTTPException(status_code=403, detail='You do not own this project')
    
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(project, field, value)
    db.commit()
    return project

@router.post('/{project_id}/publish')
def publish_project(project_id: int,
                    current_user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    """Publish project → generates embedding → runs matching."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or project.investigator_id != current_user.id:
        raise HTTPException(status_code=404, detail='Project not found')
    
    # Generate embedding
    text = ' '.join(filter(None, [project.title, project.description, project.required_skills]))
    project.embedding = json.dumps(get_embedding(text))
    project.status = 'open'
    db.commit()
    
    # Trigger matching against all mentees
    run_project_matching(project_id, db)
    return {'message': 'Project published and matching started'}

@router.delete('/{project_id}')
def close_project(project_id: int,
                  current_user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    """Close a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or project.investigator_id != current_user.id:
        raise HTTPException(status_code=404, detail='Project not found')
    
    project.status = 'closed'
    db.commit()
    return {'message': 'Project closed'}