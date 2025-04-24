from sqlalchemy.orm import Session
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserUpdate

def get_user(db: Session, user_id: int):
    """Get a single user by ID."""
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Get a single user by email."""
    return db.query(UserModel).filter(UserModel.email == email).first()

def get_user_by_username(db: Session, username: str):
    """Get a single user by username."""
    return db.query(UserModel).filter(UserModel.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get a list of users with pagination."""
    return db.query(UserModel).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    """Create a new user."""
    db_user = UserModel(
        email=user.email,
        username=user.username,
        firstName=user.firstName,
        lastName=user.lastName,
        phone=user.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    """Update an existing user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    update_data = user_update.model_dump(exclude_unset=True) # Use model_dump in Pydantic v2
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    """Delete a user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user
