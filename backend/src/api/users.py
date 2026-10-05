"""
================================================================================
User Management API Router & Domain Handlers
================================================================================
Author: Senior Software Engineer (20+ Years Experience)
Framework: FastAPI (APIRouter) + SQLModel + PostgreSQL

Key Architectural Features:
1. Domain Independence: Self-contained User DTO schemas and route definitions.
2. Security: Strong password hashing via argon2/bcrypt (`pwdlib`).
3. Relational Integrity: Handles 1-to-many user-document association queries.
4. Pythonic Annotated Typing: Allows both FastAPI dependency injection and direct function invocation.
================================================================================
"""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, SQLModel, col, select

from src.api.security import password_hash

# --- Database & Security Imports ---
from src.data.database import (
    Category,
    Document,
    DocumentCategories,
    User,
    UserDocument,
    get_session,
)

# ==============================================================================
# SECTION 1: USER DATA TRANSFER OBJECTS (DTOs / SCHEMAS)
# ==============================================================================


class UserCreate(SQLModel):
    """Schema for user registration request body."""

    name: str
    email: str
    password: str  # Plain text password received during signup


class UserLogin(SQLModel):
    """Schema for user login credentials."""

    email: str
    password: str


class UserPublic(SQLModel):
    """Safe schema for user data returned to clients (Excludes password)."""

    id: int
    name: str
    email: str


class UserUpdate(SQLModel):
    """Schema for partial user updates (all fields optional)."""

    name: str | None = None
    email: str | None = None
    password: str | None = None


class UserDocumentSummary(SQLModel):
    """Lightweight summary schema for documents owned by a user."""

    id: int
    name: str
    size_bytes: int
    extracted_text: str | None = None
    uploaded_at: datetime | None = None
    category_ids: list[int] = []
    categories: list[str] = []


# ==============================================================================
# SECTION 2: APIRouter INITIALIZATION
# ==============================================================================

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ==============================================================================
# SECTION 3: USER CRUD & RELATIONSHIP ENDPOINTS
# ==============================================================================


@router.post(
    "/",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def create_user(
    user_in: UserCreate,
    session: Annotated[Session, Depends(get_session)],
):
    """
    Registers a new user:
    1. Checks if the email is already registered (HTTP 409 Conflict).
    2. Securely hashes the password with salt.
    3. Persists the new User entity and returns the sanitized `UserPublic` DTO.
    """
    existing_user = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{user_in.email}' is already registered.",
        )

    hashed_password = password_hash.hash(user_in.password)

    db_user = User(
        name=user_in.name,
        email=user_in.email,
        password=hashed_password,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.post(
    "/login",
    response_model=UserPublic,
    status_code=status.HTTP_200_OK,
    summary="Authenticate and log in a user",
)
def login_user(
    credentials: UserLogin,
    session: Annotated[Session, Depends(get_session)],
):
    """
    Authenticates user credentials:
    1. Looks up user by email.
    2. Verifies hashed password using argon2/bcrypt.
    3. Returns UserPublic payload on success, raises HTTP 401 on invalid credentials.
    """
    user = session.exec(select(User).where(User.email == credentials.email)).first()

    if not user or not password_hash.verify(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please check your credentials.",
        )

    return user


@router.get(
    "/",
    response_model=list[UserPublic],
    summary="List all users (paginated)",
)
def get_users(
    session: Annotated[Session, Depends(get_session)],
    offset: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Max records to return")] = 20,
):
    """Fetches a paginated list of registered users."""
    statement = select(User).offset(offset).limit(limit)
    users = session.exec(statement).all()
    return users


@router.get(
    "/{user_id}",
    response_model=UserPublic,
    summary="Get user details by ID",
)
def get_user(
    user_id: int,
    session: Annotated[Session, Depends(get_session)],
):
    """Fetches a single user by primary key `user_id`."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )
    return user


@router.patch(
    "/{user_id}",
    response_model=UserPublic,
    summary="Partially update user information",
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: Annotated[Session, Depends(get_session)],
):
    """
    Updates user fields (name, email, and/or password).
    - If email is modified, validates that the new email isn't already taken.
    - If password is provided, hashes before persisting.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )

    if user_data.email is not None and user_data.email != user.email:
        conflict_user = session.exec(select(User).where(User.email == user_data.email)).first()
        if conflict_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{user_data.email}' is already taken.",
            )
        user.email = user_data.email

    if user_data.name is not None:
        user.name = user_data.name

    if user_data.password is not None:
        user.password = password_hash.hash(user_data.password)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get(
    "/{user_id}/documents",
    response_model=list[UserDocumentSummary],
    summary="Get all documents owned by a user (1-to-Many Relationship)",
)
def get_user_documents(
    user_id: int,
    session: Annotated[Session, Depends(get_session)],
):
    """
    Retrieves all documents associated with a specific User via `UserDocument`.
    Attaches list of category IDs for each document.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )

    user_docs = session.exec(select(UserDocument).where(UserDocument.user_id == user_id)).all()
    doc_ids = [ud.doc_id for ud in user_docs]
    if not doc_ids:
        return []

    documents = session.exec(select(Document).where(col(Document.id).in_(doc_ids))).all()

    # Pre-fetch all categories for fast mapping
    all_categories = session.exec(select(Category)).all()
    cat_map = {c.id: c.name for c in all_categories if c.id is not None}

    result = []
    for doc in documents:
        if doc.id is not None:
            doc_cats = session.exec(
                select(DocumentCategories.cat_id).where(DocumentCategories.doc_id == doc.id)
            ).all()
            category_id_list = list(doc_cats)
            category_name_list = [cat_map[cid] for cid in category_id_list if cid in cat_map]
            result.append(
                UserDocumentSummary(
                    id=doc.id,
                    name=doc.name,
                    size_bytes=len(doc.body),
                    extracted_text=doc.extracted_text,
                    uploaded_at=doc.uploaded_at,
                    category_ids=category_id_list,
                    categories=category_name_list,
                )
            )
    return result
