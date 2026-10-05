# Tables & SQLModel Domain Models

This document references the exact Python class definitions for all ORM models implemented in `backend/src/data/database.py`.

---

## 🐍 Model Definitions

### 1. `User` Entity
```python
class User(SQLModel, table=True):
    __tablename__: str = "users"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    password: str = Field(nullable=False)
```

---

### 2. `Category` Entity & `CategoryType` Enum
```python
class CategoryType(StrEnum):
    INVOICE = "Invoice"
    CONTRACTS = "Contracts"
    REPORTS = "Reports"
    NOTES = "Notes"
    MEDICAL = "Medical"
    OTHERS = "Others"


class Category(SQLModel, table=True):
    __tablename__: str = "categories"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=50)
```

---

### 3. `Document` Entity
```python
class Document(SQLModel, table=True):
    __tablename__: str = "documents"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    body: bytes = Field(nullable=False)
    extracted_text: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    uploaded_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
```

---

### 4. `DocumentCategories` (Junction Model)
```python
class DocumentCategories(SQLModel, table=True):
    __tablename__: str = "document_categories"

    doc_id: int = Field(foreign_key="documents.id", primary_key=True)
    cat_id: int = Field(foreign_key="categories.id", primary_key=True)
```

---

### 5. `UserDocument` (Ownership Junction Model)
```python
class UserDocument(SQLModel, table=True):
    __tablename__: str = "user_document"

    user_id: int = Field(foreign_key="users.id", primary_key=True)
    doc_id: int = Field(foreign_key="documents.id", primary_key=True)
```

---

### 6. `CategoryKeyword` (Keyword Dictionary Model)
```python
class CategoryKeyword(SQLModel, table=True):
    __tablename__: str = "category_keyword"

    id: int | None = Field(default=None, primary_key=True)
    keyword: str = Field(unique=True, index=True, nullable=False, max_length=100)
    cat_id: int = Field(foreign_key="categories.id", nullable=False, index=True)
```
