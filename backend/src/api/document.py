"""
================================================================================
Document Management API Router & Domain Handlers
================================================================================
Author: Senior Software Engineer (20+ Years Experience)
Framework: FastAPI (APIRouter) + SQLModel + PostgreSQL + RapidOCR Engine

Key Architectural Features:
1. Strict Defense-in-Depth File Validation:
   - Validates PDF format via extension & %PDF magic bytes signature.
2. Dual-Pass Text Extraction:
   - Rapid digital text extraction with OCR fallback for scanned pages.
3. Binary BLOB Storage & Streaming:
   - PostgreSQL BYTEA persistence and binary streaming downloads with HTTP attachment headers.
4. Independent Domain Decoupling:
   - Self-contained DTO schemas, form data parsers, and route handlers.
5. Pythonic Annotated Typing:
   - Clean dependency injection and frictionless testability.
================================================================================
"""

import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from sqlmodel import Session, SQLModel, col, select
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger("document_service")

# --- Database & Model Imports ---
from src.data.database import (
    Category,
    CategoryType,
    Document,
    DocumentCategories,
    User,
    UserDocument,
    get_session,
)
from src.model.categorizer import (
    MultiCategoryPredictionResult,
    classify_document_multi_category,
)
from src.model.contents import InvalidFileTypeError, extract_text_from_file

# ==============================================================================
# SECTION 1: DOCUMENT DATA TRANSFER OBJECTS (DTOs / SCHEMAS)
# ==============================================================================


class CategorySummary(SQLModel):
    """Category summary schema embedded inside document responses."""

    id: int
    name: str


class DocumentPublic(SQLModel):
    """
    Lightweight schema for document listing.
    Excludes binary BLOB data to ensure high-performance pagination.
    """

    id: int
    name: str
    size_bytes: int
    extracted_text: str | None = None
    uploaded_at: datetime | None = None
    category_ids: list[int] = []


class DocumentDetailPublic(SQLModel):
    """
    Comprehensive document detail schema including ownership,
    full category metadata, extracted OCR text, and ML classification diagnostics.
    """

    id: int
    name: str
    size_bytes: int
    extracted_text: str | None = None
    uploaded_at: datetime | None = None
    owner_user_id: int | None = None
    categories: list[CategorySummary] = []
    predicted_category: str | None = None
    prediction_confidence: float | None = None
    matched_keywords: list[str] = []


class DocumentUpdate(SQLModel):
    """Schema for partial document updates."""

    name: str | None = None
    category_ids: list[int] | None = None


# ==============================================================================
# SECTION 2: HELPER UTILITIES & FORM PARSERS
# ==============================================================================

IGNORED_CATEGORY_TOKENS = {
    "",
    "string",
    "none",
    "null",
    "undefined",
    "[]",
    "{}",
    "0",
    "false",
    "-1",
    "n/a",
    "na",
}


def resolve_categories(
    raw_category_ids: list[str] | str | None,
    session: Session,
) -> list[Category]:
    """
    Flexible Category Resolver:
    Gracefully accepts:
    - Integer IDs: [1, 2], ['1', '2']
    - Category Names & Aliases (case-insensitive, singular/plural): 'Invoice', 'invoices', 'contract', 'Contracts', 'Notes'
    - Swagger UI / Form defaults: '', [''], 'string', 'null', 'none' (safely ignored)
    - Returns matching Category entities from the database.
    """
    if not raw_category_ids:
        return []

    items: list[str] = []
    if isinstance(raw_category_ids, str):
        cleaned = raw_category_ids.strip("[]").strip()
        if cleaned:
            items = [item.strip().strip("'\"") for item in cleaned.split(",") if item.strip()]
    elif isinstance(raw_category_ids, list):
        for entry in raw_category_ids:
            if isinstance(entry, int):
                items.append(str(entry))
            elif isinstance(entry, str):
                cleaned = entry.strip("[]").strip()
                if cleaned:
                    items.extend(
                        [item.strip().strip("'\"") for item in cleaned.split(",") if item.strip()]
                    )

    # Filter out Swagger placeholders, empty strings, and null tokens
    items = [item for item in items if item and item.strip().lower() not in IGNORED_CATEGORY_TOKENS]
    if not items:
        return []

    # Fetch all categories available in the database for intelligent matching
    all_categories = session.exec(select(Category)).all()
    id_map = {cat.id: cat for cat in all_categories}

    # Build flexible name & alias mapping
    name_map = {}
    for cat in all_categories:
        cat_str = cat.name.lower()
        name_map[cat_str] = cat
        # Singular & Plural aliases
        if cat_str.endswith("s"):
            name_map[cat_str[:-1]] = cat
        else:
            name_map[f"{cat_str}s"] = cat

    # Also map standard CategoryType Enum definitions
    for cat_enum in CategoryType:
        enum_val = cat_enum.value.lower()
        matching_cat = next((c for c in all_categories if c.name.lower() == enum_val), None)
        if matching_cat:
            name_map[cat_enum.name.lower()] = matching_cat
            name_map[enum_val] = matching_cat
            if enum_val.endswith("s"):
                name_map[enum_val[:-1]] = matching_cat
            else:
                name_map[f"{enum_val}s"] = matching_cat

    resolved: list[Category] = []
    seen_ids = set()

    for item in items:
        matched: Category | None = None
        cleaned_item = item.strip().lower()

        # 1. Try numeric ID lookup
        if cleaned_item.isdigit():
            num_id = int(cleaned_item)
            if num_id in id_map:
                matched = id_map[num_id]

        # 2. Try Name & Alias lookup (case-insensitive, singular/plural)
        if not matched and cleaned_item in name_map:
            matched = name_map[cleaned_item]

        # 3. Try CategoryType Enum parsing with built-in alias mapping (_missing_)
        if not matched:
            try:
                enum_match = CategoryType(cleaned_item)
                if enum_match:
                    target_name = enum_match.value.lower()
                    if target_name in name_map:
                        matched = name_map[target_name]
            except (ValueError, KeyError, Exception):
                pass

        # 4. Substring / Prefix fuzzy lookup
        if not matched:
            for key, cat in name_map.items():
                if len(cleaned_item) >= 3 and (
                    key.startswith(cleaned_item) or cleaned_item.startswith(key)
                ):
                    matched = cat
                    break

        if not matched:
            available_info = [f"ID {cat.id}: '{cat.name}'" for cat in all_categories]
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Category '{item}' not found. "
                    f"Available categories in database: [{', '.join(available_info)}]."
                ),
            )

        if matched.id not in seen_ids:
            seen_ids.add(matched.id)
            resolved.append(matched)

    return resolved


# ==============================================================================
# SECTION 3: APIRouter INITIALIZATION
# ==============================================================================

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


# ==============================================================================
# SECTION 4: DOCUMENT MANAGEMENT ENDPOINTS
# ==============================================================================


@router.post(
    "/",
    response_model=DocumentDetailPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new PDF document with OCR text extraction",
)
async def upload_document(
    file: Annotated[UploadFile, File(description="PDF Document file to upload (.pdf)")],
    session: Annotated[Session, Depends(get_session)],
    owner_user_id: Annotated[
        int | None, Form(description="Optional User ID to assign ownership")
    ] = None,
    category_ids: Annotated[
        list[str] | None,
        Form(description="Optional Category IDs or Names (e.g. 10, 'Invoice')"),
    ] = None,
):
    """
    Uploads and processes a PDF document:
    1. Validates strictly that the file is a PDF (extension & magic byte signature).
    2. Runs RapidOCR dual-pass text extraction.
    3. Persists document binary BLOB into PostgreSQL.
    4. Links document ownership (1-to-many) if `owner_user_id` is supplied.
    5. Associates document categories (many-to-many) if `category_ids` are supplied.
    """
    file_bytes = await file.read()
    filename = file.filename or "document.pdf"

    # Step 1 & 2: Validate PDF & Extract OCR Text (offloaded from main async event loop)
    try:
        extracted_text = await run_in_threadpool(
            extract_text_from_file, file_bytes=file_bytes, filename=filename
        )
    except InvalidFileTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error(f"Document text extraction failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document text extraction and processing failed.",
        ) from exc

    # Step 3: Execute Multi-Category Keyword Matching & Classification
    multi_prediction: MultiCategoryPredictionResult | None = None
    if extracted_text:
        try:
            multi_prediction = classify_document_multi_category(
                text=extracted_text, session=session
            )
        except Exception as exc:
            # Resilient degradation: log error without breaking document upload
            logger.warning(f"Document classification warning: {exc}")

    try:
        # Step 4: Validate optional owner user
        if owner_user_id is not None:
            user = session.get(User, owner_user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Owner user with ID {owner_user_id} not found.",
                )

        # Step 5: Parse & validate explicit category IDs / Names OR Auto-Assign via Keyword Mapping Engine
        valid_categories = []
        if category_ids:
            # Client provided explicit manual category selection
            valid_categories = resolve_categories(category_ids, session)

        # Auto-assign all matched categories from keyword engine (or 'Others' fallback)
        if not valid_categories:
            if multi_prediction and multi_prediction.categories:
                for cat_detail in multi_prediction.categories:
                    if cat_detail.category_id:
                        cat_obj = session.get(Category, cat_detail.category_id)
                        if cat_obj and cat_obj not in valid_categories:
                            valid_categories.append(cat_obj)

            # If still empty (e.g. no DB records), fallback to Others category directly
            if not valid_categories:
                others_cat = session.exec(
                    select(Category).where(Category.name == CategoryType.OTHERS.value)
                ).first()
                if others_cat:
                    valid_categories.append(others_cat)

        # Step 6: Persist Document Entity
        db_document = Document(
            name=filename,
            body=file_bytes,
            extracted_text=extracted_text,
        )
        session.add(db_document)
        session.commit()
        session.refresh(db_document)
        assert db_document.id is not None

        # Step 7: Persist User Ownership mapping
        if owner_user_id is not None:
            user_doc = UserDocument(user_id=owner_user_id, doc_id=db_document.id)
            session.add(user_doc)

        # Step 8: Persist Category Mappings (Many-to-Many)
        for cat in valid_categories:
            if cat.id is not None:
                doc_cat = DocumentCategories(doc_id=db_document.id, cat_id=cat.id)
                session.add(doc_cat)

        session.commit()

        # Resolve primary category name and confidence
        primary_category_name = (
            multi_prediction.primary_category
            if multi_prediction
            else (valid_categories[0].name if valid_categories else CategoryType.OTHERS.value)
        )
        primary_confidence = (
            multi_prediction.categories[0].confidence_score
            if (multi_prediction and multi_prediction.categories)
            else 1.0
        )
        all_kws = multi_prediction.all_matched_keywords if multi_prediction else []

        return DocumentDetailPublic(
            id=db_document.id,
            name=db_document.name,
            size_bytes=len(db_document.body),
            extracted_text=db_document.extracted_text,
            uploaded_at=db_document.uploaded_at,
            owner_user_id=owner_user_id,
            categories=[
                CategorySummary(id=c.id, name=c.name) for c in valid_categories if c.id is not None
            ],
            predicted_category=primary_category_name,
            prediction_confidence=primary_confidence,
            matched_keywords=all_kws,
        )

    except HTTPException:
        session.rollback()
        raise
    except Exception as exc:
        session.rollback()
        logger.error(f"Database persistence error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist document to the database.",
        ) from exc


@router.get(
    "/",
    response_model=list[DocumentPublic],
    summary="List documents (with pagination & category filter)",
)
def get_documents(
    session: Annotated[Session, Depends(get_session)],
    offset: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Max records to return")] = 20,
    category_id: Annotated[int | None, Query(description="Optional category filter")] = None,
):
    """
    Fetches a paginated list of documents.
    Supports optional filtering by `category_id`.
    """
    if category_id is not None:
        doc_links = session.exec(
            select(DocumentCategories).where(DocumentCategories.cat_id == category_id)
        ).all()
        doc_ids = [link.doc_id for link in doc_links]
        if not doc_ids:
            return []
        statement = (
            select(Document).where(col(Document.id).in_(doc_ids)).offset(offset).limit(limit)
        )
    else:
        statement = select(Document).offset(offset).limit(limit)

    documents = session.exec(statement).all()

    result = []
    for doc in documents:
        if doc.id is not None:
            doc_cats = session.exec(
                select(DocumentCategories.cat_id).where(DocumentCategories.doc_id == doc.id)
            ).all()
            result.append(
                DocumentPublic(
                    id=doc.id,
                    name=doc.name,
                    size_bytes=len(doc.body),
                    extracted_text=doc.extracted_text,
                    uploaded_at=doc.uploaded_at,
                    category_ids=list(doc_cats),
                )
            )
    return result


@router.get(
    "/{document_id}",
    response_model=DocumentDetailPublic,
    summary="Get document details by ID",
)
def get_document(
    document_id: int,
    session: Annotated[Session, Depends(get_session)],
):
    """Fetches comprehensive metadata, extracted text, owner, and categories for a document."""
    doc = session.get(Document, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found.",
        )

    # Fetch owner user ID
    user_doc = session.exec(select(UserDocument).where(UserDocument.doc_id == document_id)).first()
    owner_user_id = user_doc.user_id if user_doc else None

    # Fetch associated categories
    cat_links = session.exec(
        select(DocumentCategories).where(DocumentCategories.doc_id == document_id)
    ).all()
    cat_ids = [link.cat_id for link in cat_links]

    categories: list[CategorySummary] = []
    if cat_ids:
        db_cats = session.exec(select(Category).where(col(Category.id).in_(cat_ids))).all()
        categories = [CategorySummary(id=c.id, name=c.name) for c in db_cats if c.id is not None]

    return DocumentDetailPublic(
        id=doc.id or document_id,
        name=doc.name,
        size_bytes=len(doc.body),
        extracted_text=doc.extracted_text,
        uploaded_at=doc.uploaded_at,
        owner_user_id=owner_user_id,
        categories=categories,
    )


@router.get(
    "/{document_id}/download",
    summary="Download original document file binary (BLOB)",
)
def download_document(
    document_id: int,
    session: Annotated[Session, Depends(get_session)],
):
    """
    Streams the raw binary BLOB stored in PostgreSQL as a file download
    with proper `Content-Disposition` headers and `application/pdf` MIME type.
    """
    doc = session.get(Document, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found.",
        )

    return Response(
        content=doc.body,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{doc.name}"',
            "Content-Length": str(len(doc.body)),
        },
    )


@router.patch(
    "/{document_id}",
    response_model=DocumentDetailPublic,
    summary="Partially update document metadata or categories",
)
def update_document(
    document_id: int,
    doc_data: DocumentUpdate,
    session: Annotated[Session, Depends(get_session)],
):
    """
    Updates document name and/or re-associates category IDs.
    """
    doc = session.get(Document, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found.",
        )

    if doc_data.name is not None:
        doc.name = doc_data.name
        session.add(doc)

    if doc_data.category_ids is not None:
        # Validate all provided categories
        for cat_id in doc_data.category_ids:
            cat = session.get(Category, cat_id)
            if not cat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category with ID {cat_id} not found.",
                )

        # Clear existing category links
        existing_links = session.exec(
            select(DocumentCategories).where(DocumentCategories.doc_id == document_id)
        ).all()
        for link in existing_links:
            session.delete(link)

        # Insert new category links
        for cat_id in doc_data.category_ids:
            session.add(DocumentCategories(doc_id=document_id, cat_id=cat_id))

    session.commit()
    session.refresh(doc)

    # Return refreshed detail
    return get_document(document_id=document_id, session=session)
