from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import random, string
import models, schemas
import auth_utils as auth
from database import get_db

router = APIRouter(prefix="/api/links", tags=["Links"])

def generate_slug(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

@router.post("", response_model=schemas.LinkDetail)
def create_link(
    link_data: schemas.LinkCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not current_user.is_pro:
        link_count = db.query(models.Link).filter(models.Link.owner_id == current_user.id).count()
        if link_count >= 5:
            raise HTTPException(status_code=403, detail="Free tier limit reached. Upgrade to Pro.")

    if link_data.custom_slug:
        slug = link_data.custom_slug
        if db.query(models.Link).filter(models.Link.slug == slug).first():
            raise HTTPException(status_code=400, detail="Slug already taken")
    else:
        slug = generate_slug()
        while db.query(models.Link).filter(models.Link.slug == slug).first():
            slug = generate_slug()

    new_link = models.Link(
        slug=slug,
        original_url=link_data.url,
        owner_id=current_user.id
    )
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    
    return schemas.LinkDetail(
        id=new_link.id,
        slug=new_link.slug,
        original_url=new_link.original_url,
        clicks=new_link.clicks,
        created_at=new_link.created_at,
        short_url=f"linkforge.io/{new_link.slug}"
    )

@router.get("", response_model=List[schemas.LinkOut])
def get_links(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    offset = (page - 1) * limit
    links = db.query(models.Link)\
        .filter(models.Link.owner_id == current_user.id)\
        .order_by(models.Link.created_at.desc())\
        .offset(offset).limit(limit).all()
    return links

@router.get("/{link_id}", response_model=schemas.LinkDetail)
def get_link_detail(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    link = db.query(models.Link).filter(
        models.Link.id == link_id,
        models.Link.owner_id == current_user.id
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return schemas.LinkDetail(
        id=link.id,
        slug=link.slug,
        original_url=link.original_url,
        clicks=link.clicks,
        created_at=link.created_at,
        short_url=f"linkforge.io/{link.slug}"
    )

@router.delete("/{link_id}")
def delete_link(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    link = db.query(models.Link).filter(
        models.Link.id == link_id,
        models.Link.owner_id == current_user.id
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    db.delete(link)
    db.commit()
    return {"msg": "Link deleted successfully"}
