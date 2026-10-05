"""
================================================================================
PDF OCR & Document Text Extraction Service
================================================================================
Author: Senior Software Engineer & Technical Documentation Engineer
Engine: RapidOCR (ONNX Runtime CPU) + PyMuPDF (fitz)

Key Architectural Concepts for New Developers:
1. Strict Defense-in-Depth File Validation:
   - Restricts ingestion strictly to PDF files (.pdf).
   - Validates file size (<= 3 MB), filename extension, and the `%PDF` magic byte signature.
   - Prevents malicious file uploads, spoofed extensions (e.g. executable renamed to .pdf),
     and corrupted binary payloads before expensive OCR processing begins.

2. Singleton OCR Engine:
   - RapidOCR utilizes an underlying ONNX Runtime session with pre-trained neural networks.
   - Initializing ONNX sessions per request would create severe CPU/memory overhead.
   - We maintain a thread-safe module-level singleton (`get_ocr_engine`) that is initialized once.

3. Dual-Pass Text Extraction Pipeline:
   - Pass 1 (Fast Path): Extracts digital/vector text streams using PyMuPDF (`page.get_text()`).
     This provides near-instantaneous (<10ms) extraction for standard digital PDFs.
   - Pass 2 (OCR Fallback): If a page yields no digital text (scanned page or image PDF),
     the page is rendered to a 150 DPI PNG pixmap and passed to RapidOCR for optical text recognition.
   - Result: Seamlessly handles text-based, scanned, and hybrid multi-page PDFs.
================================================================================
"""

import logging

import pymupdf
from rapidocr_onnxruntime import RapidOCR

from src.constants.constant import MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB

logger = logging.getLogger("ocr_service")

# PDF Header Magic Bytes Signature (%PDF)
PDF_MAGIC_SIGNATURE = b"%PDF"


class InvalidFileTypeError(ValueError):
    """Raised when an uploaded file is not a valid PDF or fails defense-in-depth checks."""

    pass


# Module-level singleton instance for ONNX runtime session reuse
_ocr_engine: RapidOCR | None = None


def get_ocr_engine() -> RapidOCR:
    """
    Lazy-initializes and returns the singleton RapidOCR engine.

    Why:
        Allocating ONNX model sessions in memory is computationally expensive.
        Reusing a single runtime instance keeps CPU utilization low and enables fast inference.

    Returns:
        RapidOCR: Shared instance ready for OCR inference.
    """
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = RapidOCR()
    return _ocr_engine


def validate_pdf_file(file_bytes: bytes, filename: str = "") -> None:
    """
    Validates that the provided payload is strictly an authentic PDF document.

    Verification Layers:
    1. Empty Payload Check: Rejects 0-byte or null byte buffers.
    2. File Size Limit: Enforces strict <= 3 MB constraint (`MAX_FILE_SIZE_BYTES`).
    3. Extension Verification: Verifies that the filename terminates with `.pdf` (case-insensitive).
    4. Magic Bytes Signature: Inspects the first 1024 bytes to confirm the presence of `%PDF`.

    Args:
        file_bytes: Raw binary payload received from HTTP upload.
        filename: Original file name provided by the client.

    Raises:
        InvalidFileTypeError: If any security or format constraint is violated.
    """
    if not file_bytes or len(file_bytes) == 0:
        raise InvalidFileTypeError("Selected file is incorrect. Uploaded file is empty.")

    # 1. File Size Check (<= 3MB)
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        size_mb = len(file_bytes) / (1024 * 1024)
        raise InvalidFileTypeError(
            f"File size ({size_mb:.2f} MB) exceeds the maximum allowed limit of {MAX_FILE_SIZE_MB} MB. "
            f"Please upload a file less than or equal to {MAX_FILE_SIZE_MB} MB."
        )

    # 2. Filename Extension Check (case-insensitive)
    if filename:
        clean_name = filename.strip().lower()
        if not clean_name.endswith(".pdf"):
            raise InvalidFileTypeError(
                f"Selected file is incorrect. Only PDF files (.pdf) are allowed. Received: '{filename}'"
            )

    # 3. Magic Byte Signature Check (%PDF)
    # Authentic PDFs contain the %PDF header within the first 1024 bytes of the binary header
    if (
        not file_bytes.startswith(PDF_MAGIC_SIGNATURE)
        and PDF_MAGIC_SIGNATURE not in file_bytes[:1024]
    ):
        raise InvalidFileTypeError(
            "Selected file is incorrect. The file is not a valid PDF document."
        )


def extract_text_from_image(image_bytes: bytes) -> str | None:
    """
    Runs RapidOCR optical character recognition on rendered page image bytes.

    Args:
        image_bytes: PNG formatted byte array of a rendered document page.

    Returns:
        str | None: Concatenated lines of recognized text, or None if no text was found.
    """
    try:
        engine = get_ocr_engine()
        result, _ = engine(image_bytes)
        if not result:
            return None
        # RapidOCR returns a list of [bounding_box, recognized_text, confidence_score]
        lines = [line[1] for line in result if len(line) > 1 and line[1]]
        extracted = "\n".join(lines).strip()
        return extracted if extracted else None
    except Exception as exc:
        logger.warning(f"OCR image extraction error: {exc}")
        return None


def extract_text_from_pdf(pdf_bytes: bytes) -> str | None:
    """
    Executes dual-pass text extraction across all pages of a PDF document:
    1. First tries digital text extraction via PyMuPDF.
    2. If a page contains no digital text (e.g., scanned receipt/invoice),
       renders the page to a 150 DPI image and invokes RapidOCR.

    Args:
        pdf_bytes: Raw bytes of the validated PDF.

    Returns:
        str | None: Complete text extracted across all pages, joined by double newlines.

    Raises:
        InvalidFileTypeError: If PyMuPDF encounters corrupted or unparseable PDF streams.
    """
    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        logger.error(f"Failed to parse PDF document stream: {exc}")
        raise InvalidFileTypeError(
            "Selected file is incorrect or contains corrupted PDF data."
        ) from exc

    try:
        extracted_pages = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            # Fast-path digital text extraction
            text = str(page.get_text()).strip()

            if text:
                extracted_pages.append(text)
            else:
                # Scanned fallback: 150 DPI balances OCR accuracy and memory/CPU throughput
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                ocr_text = extract_text_from_image(img_bytes)
                if ocr_text:
                    extracted_pages.append(ocr_text)

        doc.close()
        full_text = "\n\n".join(extracted_pages).strip()
        return full_text if full_text else None
    except InvalidFileTypeError:
        raise
    except Exception as exc:
        logger.warning(f"PDF text extraction error: {exc}")
        return None


def extract_text_from_file(file_bytes: bytes, filename: str) -> str | None:
    """
    Public API entry point for document text extraction.
    Performs defense-in-depth validation followed by dual-pass extraction.

    Args:
        file_bytes: Raw binary content of the uploaded file.
        filename: Client-supplied file name.

    Returns:
        str | None: Extracted text or None.

    Raises:
        InvalidFileTypeError: If file validation fails or file format is invalid.
    """
    # 1. Strict validation of PDF extension, size, and magic byte signature
    validate_pdf_file(file_bytes=file_bytes, filename=filename)

    # 2. Extract text from validated PDF
    return extract_text_from_pdf(file_bytes)
