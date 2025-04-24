from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.user import User, UserCreate, UserUpdate
from app.controllers import user_controller

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email or username already exists
    db_user_by_email = user_controller.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user_by_username = user_controller.get_user_by_username(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    return user_controller.create_user(db=db, user=user)

@router.get("/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = user_controller.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_controller.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=User)
def update_existing_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    # Check for potential conflicts if email/username are being updated
    if user.email:
        db_user_by_email = user_controller.get_user_by_email(db, email=user.email)
        if db_user_by_email and db_user_by_email.id != user_id:
            raise HTTPException(status_code=400, detail="Email already registered by another user")
    if user.username:
        db_user_by_username = user_controller.get_user_by_username(db, username=user.username)
        if db_user_by_username and db_user_by_username.id != user_id:
            raise HTTPException(status_code=400, detail="Username already taken by another user")
            
    updated_user = user_controller.update_user(db=db, user_id=user_id, user_update=user)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

# Using PATCH for partial updates might be more appropriate 
# if you want to distinguish between full and partial updates.
# For simplicity, PUT is used here to replace/update.

@router.delete("/{user_id}", response_model=User)
def delete_existing_user(user_id: int, db: Session = Depends(get_db)):
    deleted_user = user_controller.delete_user(db=db, user_id=user_id)
    if deleted_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_user

# Note: A PATCH endpoint could be added for partial updates:
# @router.patch("/{user_id}", response_model=User)
# def partially_update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
#     # Logic similar to PUT, but ensures only provided fields are updated.
#     # user_update.dict(exclude_unset=True) is key here.
#     updated_user = user_controller.update_user(db=db, user_id=user_id, user_update=user)
#     if updated_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return updated_user
