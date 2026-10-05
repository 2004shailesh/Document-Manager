"""
================================================================================
Category Management API Router (Read-Only Master Data)
================================================================================
Author: Senior Software Engineer (20+ Years Experience)
Framework: FastAPI (APIRouter) + SQLModel + PostgreSQL

Key Architectural Features:
1. Immutable Master Data: Static lookup table seeded on application startup.
   Strictly read-only: Only GET endpoints are exposed.
2. Master Lookup: Direct category listing and individual category retrieval.
3. Many-to-Many Traversal: Retrieves all documents mapped to a given category.
4. Pythonic Annotated Typing: Compatible with dependency injection and direct calls.
================================================================================
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, SQLModel, col, select

# --- Database Imports ---
from src.data.database import Category, Document, DocumentCategories, get_session

# ==============================================================================
# SECTION 1: CATEGORY DATA TRANSFER OBJECTS (DTOs / SCHEMAS)
# ==============================================================================


class CategoryPublic(SQLModel):
    """Schema for category responses."""

    id: int
    name: str


class CategoryDocumentSummary(SQLModel):
    """Lightweight summary schema for documents belonging to a category."""

    id: int
    name: str
    size_bytes: int
    extracted_text: str | None = None


# ==============================================================================
# SECTION 2: APIRouter INITIALIZATION
# ==============================================================================

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


# ==============================================================================
# SECTION 3: CATEGORY READ-ONLY ENDPOINTS (GET ONLY)
# ==============================================================================


@router.get(
    "/",
    response_model=list[CategoryPublic],
    summary="List all categories (paginated)",
)
def get_categories(
    session: Annotated[Session, Depends(get_session)],
    offset: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Max records to return")] = 50,
):
    """Fetches a paginated list of all statically maintained system categories."""
    statement = select(Category).offset(offset).limit(limit)
    categories = session.exec(statement).all()
    return categories


@router.get(
    "/{category_id}",
    response_model=CategoryPublic,
    summary="Get category by ID",
)
def get_category(
    category_id: int,
    session: Annotated[Session, Depends(get_session)],
):
    """Fetches a single category by primary key `category_id`."""
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found.",
        )
    return category


@router.get(
    "/{category_id}/documents",
    response_model=list[CategoryDocumentSummary],
    summary="Get all documents in a category (Many-to-Many Relationship)",
)
def get_category_documents(
    category_id: int,
    session: Annotated[Session, Depends(get_session)],
):
    """
    Retrieves all documents associated with a specific category via `DocumentCategories`.
    """
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found.",
        )

    doc_links = session.exec(
        select(DocumentCategories).where(DocumentCategories.cat_id == category_id)
    ).all()
    doc_ids = [link.doc_id for link in doc_links]
    if not doc_ids:
        return []

    documents = session.exec(select(Document).where(col(Document.id).in_(doc_ids))).all()

    return [
        CategoryDocumentSummary(
            id=doc.id,
            name=doc.name,
            size_bytes=len(doc.body),
            extracted_text=doc.extracted_text,
        )
        for doc in documents
        if doc.id is not None
    ]
