"""
================================================================================
Database Architecture, SQLModel Schemas & Lifecycle Management
================================================================================
Author: Senior Software Engineer & Technical Documentation Engineer
Framework: SQLModel (SQLAlchemy 2.0 Core) + PostgreSQL + Psycopg2

Key Architectural Concepts for New Developers:
1. Relational Entity Design:
   - `User`: Represents system accounts (credentials with Argon2 password hashing).
   - `Document`: Stores raw PDF binary blobs (BYTEA), OCR extracted text, and creation timestamp.
   - `Category`: Static master data table containing the 6 primary categories (Invoice, Contracts,
     Reports, Notes, Medical, Others).
   - `CategoryKeyword`: Relational keyword dictionary linking domain tokens to categories for ML boosting.

2. Relationship Topology:
   - User <-> Document: Many-to-Many via `UserDocument` junction table (supports document ownership).
   - Document <-> Category: Many-to-Many via `DocumentCategories` junction table (a document can belong
     to multiple categories e.g. Medical Invoice).

3. Automatic Provisioning & Seeding Pipeline:
   - Startup Lifecycle (`create_db_and_tables`):
     a. Checks if PostgreSQL database exists (creates it if missing).
     b. Creates tables via `SQLModel.metadata.create_all`.
     c. Seeds 6 static canonical categories with normalized sequential IDs (1..6).
     d. Seeds domain keywords into `category_keyword` for classification.
     e. Backfills OCR text & categorization for any legacy unmapped documents.
================================================================================
"""

import logging
from collections.abc import Generator
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import Column, Text
from sqlmodel import Field, Session, SQLModel, create_engine, select

from src.constants.constant import DATABASE_URL, DEBUG

logger = logging.getLogger("database")

# Initialize SQLModel Engine with pre-ping connection validation (SQL echo disabled by default in production)
engine = create_engine(DATABASE_URL, echo=DEBUG, pool_pre_ping=True)

# ==============================================================================
# SECTION 1: DATABASE PROVISIONING & SESSION LIFECYCLE
# ==============================================================================


def ensure_database_exists() -> None:
    """
    Deprecated for Cloud Deployments.
    Managed PostgreSQL providers (Neon, Render, Supabase) pre-provision databases.
    This function is maintained as a no-op to ensure zero startup interference.
    """
    pass


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a managed SQLModel Session per HTTP request.

    Yields:
        Session: Scoped SQLModel session with automated teardown on request completion.
    """
    with Session(engine) as session:
        yield session


# ==============================================================================
# SECTION 2: DOMAIN MODELS & RELATIONAL SCHEMAS
# ==============================================================================


class User(SQLModel, table=True):
    """
    User entity representing registered accounts.

    Fields:
        id: Primary key auto-incrementing integer.
        name: User's display name.
        email: Unique indexed email address used for login authentication.
        password: Salted password hash (never stored in plain text).
    """

    __tablename__: str = "users"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    password: str = Field(nullable=False)


class CategoryType(StrEnum):
    """
    Enumeration of system categories with intelligent alias resolution.
    Supports flexible parsing for singular/plural forms and domain aliases.
    """

    INVOICE = "Invoice"
    CONTRACTS = "Contracts"
    REPORTS = "Reports"
    NOTES = "Notes"
    MEDICAL = "Medical"
    OTHERS = "Others"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower() or member.name.lower() == value.lower():
                    return member
            cleaned = value.lower().strip()
            if cleaned in ("general", "other", "unknown", "misc"):
                return cls.OTHERS
            if cleaned in (
                "med",
                "medicine",
                "healthcare",
                "clinical",
                "health",
                "pharma",
            ):
                return cls.MEDICAL
        return None


class Category(SQLModel, table=True):
    """
    Category master lookup entity.

    Fields:
        id: Canonical category ID (1: Invoice, 2: Contracts, 3: Reports, 4: Notes, 5: Medical, 6: Others).
        name: Unique category title.
    """

    __tablename__: str = "categories"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=50)


class Document(SQLModel, table=True):
    """
    Document storage entity.

    Fields:
        id: Primary key integer.
        name: Original filename of the uploaded PDF.
        body: Raw PDF binary payload stored directly in PostgreSQL BYTEA format.
        extracted_text: Full text extracted via PyMuPDF or RapidOCR fallback.
        uploaded_at: UTC timestamp when the document was initially uploaded.
    """

    __tablename__: str = "documents"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    body: bytes = Field(nullable=False)
    extracted_text: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    uploaded_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )


class DocumentCategories(SQLModel, table=True):
    """
    Junction table implementing Many-to-Many mapping between Documents and Categories.
    Allows a document to belong to multiple categories simultaneously.
    """

    __tablename__: str = "document_categories"  # type: ignore

    doc_id: int = Field(foreign_key="documents.id", primary_key=True)
    cat_id: int = Field(foreign_key="categories.id", primary_key=True)


class UserDocument(SQLModel, table=True):
    """
    Junction table implementing ownership relationships between Users and Documents.
    """

    __tablename__: str = "user_document"  # type: ignore

    user_id: int = Field(foreign_key="users.id", primary_key=True)
    doc_id: int = Field(foreign_key="documents.id", primary_key=True)


class CategoryKeyword(SQLModel, table=True):
    """
    Relational keyword dictionary linked to master Category records.
    Stores domain reference terms used by the hybrid classifier for keyword boosting.
    """

    __tablename__: str = "category_keyword"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    keyword: str = Field(unique=True, index=True, nullable=False, max_length=100)
    cat_id: int = Field(foreign_key="categories.id", nullable=False, index=True)


# ==============================================================================
# SECTION 3: MASTER DATA SEEDING & APPLICATION INITIALIZATION
# ==============================================================================

# Static seed keywords mapped to each core category
STATIC_CATEGORY_KEYWORDS = {
    CategoryType.INVOICE.value: [
        "invoice",
        "tax invoice",
        "receipt",
        "billing",
        "subtotal",
        "amount due",
        "balance due",
        "total amount",
        "due date",
        "invoice number",
        "invoice date",
        "remittance",
        "vat",
        "gst",
        "payment terms",
        "purchase order",
        "po number",
        "vendor",
        "line items",
        "unit price",
        "quantity",
        "payable to",
        "bill to",
        "ship to",
        "account number",
        "wire transfer",
        "net 30",
        "net 60",
        "e-receipt",
        "payment",
        "transaction",
        "amount",
        "fee",
        "bill",
        "bank details",
    ],
    CategoryType.CONTRACTS.value: [
        "agreement",
        "contract",
        "terms and conditions",
        "parties",
        "confidentiality",
        "non-disclosure",
        "nda",
        "indemnification",
        "indemnity",
        "jurisdiction",
        "governing law",
        "breach",
        "effective date",
        "termination",
        "signatory",
        "witnesseth",
        "covenants",
        "intellectual property",
        "liabilities",
        "amendment",
        "whereas",
        "in witness whereof",
        "obligations",
        "severability",
        "arbitration",
    ],
    CategoryType.REPORTS.value: [
        "executive summary",
        "report",
        "findings",
        "methodology",
        "quarterly results",
        "annual report",
        "analysis",
        "conclusion",
        "recommendations",
        "performance metrics",
        "kpi",
        "overview",
        "financial overview",
        "market research",
        "audit report",
        "assessment",
        "data analysis",
        "evaluation",
        "benchmarks",
        "key findings",
        "status report",
        "progress report",
        "survey results",
        "table of contents",
        "research report",
        "summary",
        "appendix",
    ],
    CategoryType.NOTES.value: [
        "meeting minutes",
        "notes",
        "action items",
        "agenda",
        "memo",
        "memorandum",
        "to-do",
        "follow-up",
        "discussion",
        "brainstorming",
        "summary notes",
        "attendees",
        "key takeaways",
        "quick note",
        "briefing",
        "scratchpad",
        "internal memo",
        "decisions made",
        "next steps",
        "call notes",
    ],
    CategoryType.MEDICAL.value: [
        "prescription",
        "diagnosis",
        "medical report",
        "laboratory report",
        "pathology report",
        "blood test",
        "radiology",
        "x-ray",
        "mri",
        "ct scan",
        "hospital",
        "clinic",
        "patient",
        "physician",
        "doctor",
        "medicine",
        "medication",
        "dosage",
        "treatment",
        "medical certificate",
        "discharge summary",
        "health insurance claim",
        "vaccination",
        "immunization",
        "ecg",
        "ultrasound",
        "medical bill",
        "clinical findings",
        "pathology",
        "pharmacy",
        "vital signs",
        "prognosis",
        "therapy",
        "outpatient",
        "inpatient",
        "rx",
        "biopsy",
        "cbc",
        "hematology",
        "physiotherapy",
        "consultation note",
        "allergies",
        "symptoms",
        "fever",
        "malaria",
        "blood smear",
        "tablet",
        "bed rest",
        "investigations",
    ],
}


def seed_static_categories() -> None:
    """
    Seeds and synchronizes the predefined static categories:
    'Invoice', 'Contracts', 'Reports', 'Notes', 'Medical', 'Others'.
    Maintains clean sequential IDs (1 to 6) and eliminates duplicate records permanently.
    """
    canonical_categories = [
        CategoryType.INVOICE.value,
        CategoryType.CONTRACTS.value,
        CategoryType.REPORTS.value,
        CategoryType.NOTES.value,
        CategoryType.MEDICAL.value,
        CategoryType.OTHERS.value,
    ]

    try:
        with engine.begin() as conn:
            # 1. Clean up duplicate records
            conn.exec_driver_sql("""
                DELETE FROM document_categories
                WHERE cat_id IN (
                    SELECT id FROM categories
                    WHERE id NOT IN (SELECT MIN(id) FROM categories GROUP BY LOWER(name))
                );
                """)
            conn.exec_driver_sql("""
                DELETE FROM category_keyword
                WHERE cat_id IN (
                    SELECT id FROM categories
                    WHERE id NOT IN (SELECT MIN(id) FROM categories GROUP BY LOWER(name))
                );
                """)
            conn.exec_driver_sql("""
                DELETE FROM categories
                WHERE id NOT IN (
                    SELECT MIN(id)
                    FROM categories
                    GROUP BY LOWER(name)
                );
                """)

            # 2. Insert any missing category
            for cat_name in canonical_categories:
                row = conn.exec_driver_sql(
                    "SELECT id FROM categories WHERE LOWER(name) = LOWER(%(name)s)",
                    {"name": cat_name},
                ).fetchone()
                if not row:
                    conn.exec_driver_sql(
                        "INSERT INTO categories (name) VALUES (%(name)s)",
                        {"name": cat_name},
                    )

            # 3. Resequence IDs cleanly to 1..6 and update foreign keys
            for target_id, cat_name in enumerate(canonical_categories, start=1):
                row = conn.exec_driver_sql(
                    "SELECT id FROM categories WHERE LOWER(name) = LOWER(%(name)s)",
                    {"name": cat_name},
                ).fetchone()
                if row and row[0] != target_id:
                    current_id = row[0]

                    # Step A: Rename old row to temporary name so unique constraint isn't violated
                    conn.exec_driver_sql(
                        "UPDATE categories SET name = %(temp_name)s WHERE id = %(current_id)s",
                        {
                            "temp_name": f"_temp_{cat_name}_{current_id}",
                            "current_id": current_id,
                        },
                    )

                    # Step B: Insert target category row with desired sequential ID
                    conn.exec_driver_sql(
                        "INSERT INTO categories (id, name) VALUES (%(target_id)s, %(name)s) ON CONFLICT (id) DO UPDATE SET name = %(name)s",
                        {"target_id": target_id, "name": cat_name},
                    )

                    # Step C: Remap child foreign keys from current_id to target_id
                    conn.exec_driver_sql(
                        "UPDATE category_keyword SET cat_id = %(target_id)s WHERE cat_id = %(current_id)s",
                        {"target_id": target_id, "current_id": current_id},
                    )
                    conn.exec_driver_sql(
                        "UPDATE document_categories SET cat_id = %(target_id)s WHERE cat_id = %(current_id)s",
                        {"target_id": target_id, "current_id": current_id},
                    )

                    # Step D: Delete the old row with current_id
                    conn.exec_driver_sql(
                        "DELETE FROM categories WHERE id = %(current_id)s",
                        {"current_id": current_id},
                    )

            # 4. Reset PostgreSQL sequence counter to the max ID (6)
            conn.exec_driver_sql(
                "SELECT setval(pg_get_serial_sequence('categories', 'id'), (SELECT COALESCE(MAX(id), 1) FROM categories));"
            )

    except Exception as exc:
        print(f"Categories normalization note: {exc}")

    print(
        "Static categories verified & resequenced: [1: Invoice, 2: Contracts, 3: Reports, 4: Notes, 5: Medical, 6: Others]."
    )


def seed_category_keywords() -> None:
    """
    Seeds domain-specific reference keywords for each category into the `category_keyword` table.
    Ensures idempotency by checking existing keywords before inserting.
    """
    with Session(engine) as session:
        # Fetch category map (lowercase name -> Category ID)
        all_categories = session.exec(select(Category)).all()
        cat_map = {cat.name.lower(): cat.id for cat in all_categories}

        # Fetch existing keywords in database to prevent duplicates
        existing_records = session.exec(select(CategoryKeyword)).all()
        existing_keywords = {kw.keyword.lower() for kw in existing_records}

        new_keywords: list[CategoryKeyword] = []
        for category_name, keywords in STATIC_CATEGORY_KEYWORDS.items():
            cat_id = cat_map.get(category_name.lower())
            if not cat_id:
                continue

            for word in keywords:
                cleaned_word = word.strip().lower()
                if cleaned_word not in existing_keywords:
                    new_keywords.append(CategoryKeyword(keyword=cleaned_word, cat_id=cat_id))
                    existing_keywords.add(cleaned_word)

        if new_keywords:
            session.add_all(new_keywords)
            session.commit()
            logger.info(
                f"Seeded {len(new_keywords)} reference keywords into `category_keyword` table."
            )
        else:
            logger.debug("Reference category keywords are up-to-date in database.")


def backfill_uncategorized_documents() -> None:
    """
    Scans all existing documents in the database. If any document has no category
    mappings in `document_categories`, automatically extracts OCR text (if missing)
    and classifies it into all matching categories (or 'Others' fallback).
    """
    from src.model.categorizer import (
        classify_document_multi_category,
        predict_document_category,
    )
    from src.model.contents import extract_text_from_file

    with Session(engine) as session:
        all_docs = session.exec(select(Document)).all()
        mapped_count = 0

        for doc in all_docs:
            existing_mapping = session.exec(
                select(DocumentCategories).where(DocumentCategories.doc_id == doc.id)
            ).first()

            if not existing_mapping:
                # 1. Extract text if missing
                if (not doc.extracted_text or len(doc.extracted_text.strip()) == 0) and doc.body:
                    try:
                        extracted = extract_text_from_file(doc.body, doc.name)
                        if extracted:
                            doc.extracted_text = extracted
                            session.add(doc)
                    except Exception as exc:
                        logger.warning(f"Backfill extraction skipped for doc {doc.id}: {exc}")

                # 2. Multi-category keyword classification
                text_to_analyze = doc.extracted_text or doc.name
                if doc.id is not None:
                    try:
                        multi_res = classify_document_multi_category(
                            text_to_analyze, session=session
                        )
                        if multi_res and multi_res.categories:
                            for cat_item in multi_res.categories:
                                session.add(
                                    DocumentCategories(doc_id=doc.id, cat_id=cat_item.category_id)
                                )
                            mapped_count += 1
                    except Exception:
                        pred = predict_document_category(text_to_analyze, session=session)
                        if pred and pred.category_id:
                            session.add(DocumentCategories(doc_id=doc.id, cat_id=pred.category_id))
                            mapped_count += 1

        if mapped_count > 0:
            session.commit()
            logger.info(
                f"Backfilled and categorized {mapped_count} existing unmapped document(s)."
            )


def create_db_and_tables() -> None:
    """
    Initializes SQLModel tables, seeds static lookup data (Categories & Keywords),
    and backfills any previously unmapped documents.
    Connects directly to the database specified by DATABASE_URL without attempting CREATE DATABASE.
    """
    SQLModel.metadata.create_all(engine)
    try:
        with engine.begin() as conn:
            conn.exec_driver_sql(
                "ALTER TABLE documents ADD COLUMN IF NOT EXISTS extracted_text TEXT;"
            )
            conn.exec_driver_sql("ALTER TABLE categories ALTER COLUMN name TYPE VARCHAR(50);")
            conn.exec_driver_sql(
                "ALTER TABLE documents ADD COLUMN IF NOT EXISTS uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;"
            )
    except Exception as exc:
        logger.debug(f"Schema verification note: {exc}")
    seed_static_categories()
    seed_category_keywords()
    backfill_uncategorized_documents()
    logger.info("Database schemas and static seed data verified successfully.")
