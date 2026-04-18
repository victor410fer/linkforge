from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas, models
import auth_utils as auth
from database import get_db

router = APIRouter(prefix="/api/billing", tags=["Billing"])

@router.post("/subscribe")
def subscribe(
    sub_data: schemas.SubscribeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if sub_data.plan != "pro":
        raise HTTPException(status_code=400, detail="Invalid plan")
    current_user.is_pro = True
    db.commit()
    return {"msg": "Successfully upgraded to Pro", "is_pro": True}
