# Building a Movie Streaming Platform API with FastAPI

This guide will walk you through creating a robust, scalable movie streaming platform API using FastAPI, following best practices for organization, performance, and data storage.

## Table of Contents
1. [Project Setup](#project-setup)
2. [Database Design](#database-design)
3. [Project Structure](#project-structure)
4. [Core API Implementation](#core-api-implementation)
5. [Authentication and Security](#authentication-and-security)
6. [Recommendation Engine](#recommendation-engine)
7. [Caching and Performance](#caching-and-performance)
8. [Testing](#testing)
9. [Deployment](#deployment)

## Project Setup

### Step 1: Environment Setup

First, create a virtual environment and install the necessary packages:

```bash
# Create a project directory
mkdir movie-streaming-api
cd movie-streaming-api

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install fastapi uvicorn[standard] sqlalchemy pydantic python-jose[cryptography] passlib[bcrypt] python-multipart pymongo redis pytest httpx tenacity
```

### Step 2: Create Initial Project Files

Create a `.env` file for environment variables:

```bash
touch .env
```

Add the following content to the `.env` file:

```
# PostgreSQL Configuration
POSTGRES_USER=movieapp
POSTGRES_PASSWORD=strongpassword
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=moviestreaming

# MongoDB Configuration
MONGO_CONNECTION_STRING=mongodb://localhost:27017/
MONGO_DB_NAME=moviestreaming

# JWT Authentication
SECRET_KEY=your-secret-key-generate-a-secure-one
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Database Design

For our application, we'll use:
- **PostgreSQL (Relational DB)**: For structured data like users, movies, subscriptions
- **MongoDB (NoSQL DB)**: For user watch history, recommendations, and analytics
- **Redis**: For caching frequent queries and session management

### Step 3: Database Schema Design

#### PostgreSQL Schema

Create a file `app/db/models.py`:

```python
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Association table for many-to-many relationship between movies and genres
movie_genre = Table(
    "movie_genre",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id")),
    Column("genre_id", Integer, ForeignKey("genres.id"))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subscriptions = relationship("Subscription", back_populates="user")

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    release_year = Column(Integer, index=True)
    duration_minutes = Column(Integer)
    poster_url = Column(String)
    video_url = Column(String)
    average_rating = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    genres = relationship("Genre", secondary=movie_genre, back_populates="movies")
    ratings = relationship("Rating", back_populates="movie")

class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    movies = relationship("Movie", secondary=movie_genre, back_populates="genres")

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    rating = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    movie = relationship("Movie", back_populates="ratings")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_name = Column(String)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="subscriptions")
```

#### MongoDB Collections

We'll create the following collections:
- `watch_history`: User viewing history
- `recommendations`: Personalized movie recommendations
- `analytics`: User behavior and platform metrics

## Project Structure

### Step 4: Set Up Project Structure

Create the following directory structure:

```
movie-streaming-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI application entry point
│   ├── config.py             # Configuration settings
│   ├── dependencies.py       # Dependency injection
│   │
│   ├── api/                  # API routes
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   ├── movies.py
│   │   │   ├── users.py
│   │   │   ├── auth.py
│   │   │   ├── watch_history.py
│   │   │   └── recommendations.py
│   │   └── router.py         # API router configuration
│   │
│   ├── core/                 # Core application logic
│   │   ├── __init__.py
│   │   ├── security.py       # Authentication and security
│   │   └── config.py         # Configuration classes
│   │
│   ├── db/                   # Database models and connections
│   │   ├── __init__.py
│   │   ├── session.py        # Database session management
│   │   ├── models.py         # SQLAlchemy models
│   │   └── mongodb.py        # MongoDB connection
│   │
│   ├── schemas/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── movie.py
│   │   ├── user.py
│   │   ├── auth.py
│   │   └── watch_history.py
│   │
│   ├── crud/                 # CRUD operations
│   │   ├── __init__.py
│   │   ├── base.py           # Base CRUD operations
│   │   ├── movie.py
│   │   ├── user.py
│   │   └── watch_history.py
│   │
│   └── services/             # Business logic services
│       ├── __init__.py
│       ├── recommendation.py
│       └── analytics.py
│
├── tests/                    # Tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── api/
│   │   ├── test_movies.py
│   │   ├── test_users.py
│   │   └── test_auth.py
│   └── services/
│       └── test_recommendation.py
│
├── .env                      # Environment variables
├── .gitignore
├── README.md
└── requirements.txt
```

## Core API Implementation

### Step 5: Configuration Setup

Create the core configuration file `app/core/config.py`:

```python
from pydantic import BaseSettings, PostgresDsn, validator
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Movie Streaming API"
    
    # PostgreSQL
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "movieapp")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "strongpassword")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "moviestreaming")
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_postgres_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    # MongoDB
    MONGO_CONNECTION_STRING: str = os.getenv("MONGO_CONNECTION_STRING", "mongodb://localhost:27017/")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "moviestreaming")
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-generate-a-secure-one")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    class Config:
        case_sensitive = True

settings = Settings()
```

### Step 6: Database Connections

Create database connection file `app/db/session.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Create MongoDB connection file `app/db/mongodb.py`:

```python
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from pymongo import MongoClient

# Synchronous client for certain operations
mongo_client = MongoClient(settings.MONGO_CONNECTION_STRING)
mongo_db = mongo_client[settings.MONGO_DB_NAME]

# Async client for async operations
async def get_mongodb():
    client = AsyncIOMotorClient(settings.MONGO_CONNECTION_STRING)
    db = client[settings.MONGO_DB_NAME]
    try:
        yield db
    finally:
        client.close()
```

### Step 7: Authentication and Security

Create `app/core/security.py`:

```python
from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### Step 8: Set Up Pydantic Models (Schemas)

Create `app/schemas/user.py`:

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: str
    is_active: Optional[bool] = True
    is_premium: Optional[bool] = False

class UserCreate(UserBase):
    email: EmailStr
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str
```

Create `app/schemas/movie.py`:

```python
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

class GenreBase(BaseModel):
    name: str

class GenreCreate(GenreBase):
    pass

class Genre(GenreBase):
    id: int

    class Config:
        orm_mode = True

class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    release_year: int
    duration_minutes: int
    poster_url: Optional[HttpUrl] = None
    video_url: Optional[HttpUrl] = None

class MovieCreate(MovieBase):
    genre_ids: List[int]

class MovieUpdate(MovieBase):
    title: Optional[str] = None
    release_year: Optional[int] = None
    duration_minutes: Optional[int] = None
    genre_ids: Optional[List[int]] = None

class Movie(MovieBase):
    id: int
    average_rating: float = 0.0
    genres: List[Genre] = []
    created_at: datetime

    class Config:
        orm_mode = True

class MovieList(BaseModel):
    items: List[Movie]
    total: int
```

Create `app/schemas/auth.py`:

```python
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None

class Login(BaseModel):
    username: str
    password: str
```

Create `app/schemas/watch_history.py`:

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WatchHistoryEntry(BaseModel):
    user_id: int
    movie_id: int
    watched_at: datetime = datetime.utcnow()
    watched_duration: int  # Seconds watched
    completed: bool = False
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "movie_id": 42,
                "watched_at": datetime.utcnow(),
                "watched_duration": 1200,
                "completed": False
            }
        }

class WatchHistoryCreate(BaseModel):
    movie_id: int
    watched_duration: int
    completed: bool = False

class WatchHistoryResponse(BaseModel):
    movie_id: int
    title: str
    poster_url: Optional[str] = None
    watched_at: datetime
    watched_duration: int
    completed: bool
    
    class Config:
        schema_extra = {
            "example": {
                "movie_id": 42,
                "title": "The Matrix",
                "poster_url": "https://example.com/matrix.jpg",
                "watched_at": datetime.utcnow(),
                "watched_duration": 1200,
                "completed": False
            }
        }

class WatchHistoryList(BaseModel):
    items: List[WatchHistoryResponse]
    total: int
```

### Step 9: CRUD Operations

Create the base CRUD file `app/crud/base.py`:

```python
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.models import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def get_count(self, db: Session) -> int:
        return db.query(self.model).count()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
```

Create `app/crud/user.py`:

```python
from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            is_active=obj_in.is_active,
            is_premium=obj_in.is_premium
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[User]:
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active
    
    def is_premium(self, user: User) -> bool:
        return user.is_premium

user = CRUDUser(User)
```

Create `app/crud/movie.py`:

```python
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.crud.base import CRUDBase
from app.db.models import Movie, Genre, movie_genre
from app.schemas.movie import MovieCreate, MovieUpdate

class CRUDMovie(CRUDBase[Movie, MovieCreate, MovieUpdate]):
    def create_with_genres(self, db: Session, *, obj_in: MovieCreate) -> Movie:
        # Extract genre_ids from the input
        genre_ids = obj_in.genre_ids
        movie_data = obj_in.dict(exclude={"genre_ids"})
        
        # Create movie object
        db_obj = Movie(**movie_data)
        db.add(db_obj)
        db.flush()  # Get movie ID without committing
        
        # Add genres
        if genre_ids:
            genres = db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
            db_obj.genres = genres
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: Movie, obj_in: MovieUpdate
    ) -> Movie:
        # Extract genre_ids if present
        genre_ids = None
        if isinstance(obj_in, dict):
            update_data = obj_in.copy()
            genre_ids = update_data.pop("genre_ids", None)
        else:
            update_data = obj_in.dict(exclude_unset=True)
            genre_ids = update_data.pop("genre_ids", None)
        
        # Update movie fields
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        
        # Update genres if genre_ids is provided
        if genre_ids is not None:
            genres = db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
            db_obj.genres = genres
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_with_filters(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        title: Optional[str] = None,
        year: Optional[int] = None,
        genre_id: Optional[int] = None,
        sort_by: Optional[str] = None
    ) -> List[Movie]:
        query = db.query(Movie)
        
        # Apply filters
        if title:
            query = query.filter(Movie.title.ilike(f"%{title}%"))
        if year:
            query = query.filter(Movie.release_year == year)
        if genre_id:
            query = query.join(Movie.genres).filter(Genre.id == genre_id)
        
        # Apply sorting
        if sort_by:
            if sort_by == "title":
                query = query.order_by(Movie.title)
            elif sort_by == "year":
                query = query.order_by(Movie.release_year)
            elif sort_by == "rating":
                query = query.order_by(desc(Movie.average_rating))
            elif sort_by == "newest":
                query = query.order_by(desc(Movie.created_at))
        
        # Count before pagination
        total = query.count()
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        return query.all(), total
    
    def search_full_text(
        self, 
        db: Session, 
        *, 
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Movie]:
        # Basic full-text search
        search_filter = Movie.title.ilike(f"%{query}%") | Movie.description.ilike(f"%{query}%")
        db_query = db.query(Movie).filter(search_filter)
        
        total = db_query.count()
        results = db_query.offset(skip).limit(limit).all()
        
        return results, total

movie = CRUDMovie(Movie)
```

### Step 10: API Routes

Create the dependencies file `app/dependencies.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from typing import Generator

from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.schemas.auth import TokenPayload
from app.crud.user import user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_obj = user.get(db, id=token_data.sub)
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    return user_obj

def get_current_active_user(current_user = Depends(get_current_user)):
    if not user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_premium_user(current_user = Depends(get_current_active_user)):
    if not user.is_premium(current_user):
        raise HTTPException(
            status_code=403, 
            detail="Premium subscription required for this feature"
        )
    return current_user
```

Create the auth routes file `app/api/endpoints/auth.py`:

```python
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, schemas
from app.core import security
from app.core.config import settings
from app.db.session import get_db

router = APIRouter()

@router.post("/login", response_model=schemas.auth.Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=schemas.user.User)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.user.UserCreate,
) -> Any:
    """
    Register a new user.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists",
        )
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this username already exists",
        )
    user = crud.user.create(db, obj_in=user_in)
    return user
```

Create the movie routes file `app/api/endpoints/movies.py`:

```python
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import redis

from app import crud, schemas
from app.db.session import get_db
from app.dependencies import get_current_active_user
from app.core.config import settings

# Initialize Redis client
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

router = APIRouter()

@router.get("/", response_model=schemas.movie.MovieList)
def get_movies(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    title: Optional[str] = None,
    year: Optional[int] = None,
    genre_id: Optional[int] = None,
    sort_by: Optional[str] = Query(None, enum=["title", "year", "rating", "newest"]),
    current_user: schemas.user.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve movies with optional filtering.
    """
    # Check cache for common queries
    cache_key = f"movies:filters:{title}:{year}:{genre_id}:{sort_by}:{skip}:{limit}"
    cached_result = redis_client.get(cache_key)