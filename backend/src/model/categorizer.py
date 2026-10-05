"""
================================================================================
Document Classification Engine: Hybrid Machine Learning & Domain Keyword Boosting
================================================================================
Author: Senior Software Engineer & Technical Documentation Engineer
Framework: Scikit-Learn (TF-IDF + Multinomial Naive Bayes) + PostgreSQL Keyword Dictionary

Key Architectural Concepts for New Developers:
1. Hybrid Classification Strategy:
   - Base ML Model: TF-IDF unigram/bigram vectorizer (sublinear TF scaling) paired with
     a Multinomial Naive Bayes probabilistic classifier trained on a calibrated domain corpus.
   - Dynamic PostgreSQL Keyword Boosting: Queries the relational `category_keyword` table
     to scan for exact domain terminology (e.g. "invoice date", "indemnification", "prescription").
   - Blended Scoring Formula:
     `Final Score = (0.60 * ML Probability) + (0.40 * Keyword Density Ratio)`
     This provides high statistical generalization while ensuring exact business keyword matches
     receive immediate high-confidence classification.

2. Multi-Category Assignment (`predict_multi`):
   - Real-world documents can belong to multiple domains (e.g., a "Medical Equipment Invoice"
     matches both "Medical" and "Invoice").
   - Returns all matching categories sorted descending by keyword hit count.
   - If no domain keywords or ML signals are detected, safely falls back to the "Others" category.
================================================================================
"""

import logging
import re
from collections.abc import Sequence
from dataclasses import dataclass, field

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sqlalchemy import func
from sqlmodel import Session, select

from src.constants.constant import MAX_MATCHED_KEYWORDS, ML_CONFIDENCE_THRESHOLD
from src.data.database import Category, CategoryKeyword, CategoryType

logger = logging.getLogger("ml_categorizer")


@dataclass
class PredictionResult:
    """
    Structured outcome for single-category document classification.

    Fields:
        predicted_category: Name of winning category (e.g., 'Invoice').
        category_id: Canonical integer ID in the database.
        confidence: Combined hybrid confidence score (0.0 to 1.0).
        matched_keywords: Top diagnostic keywords detected in document text.
        probabilities: Full probability distribution across all categories.
    """

    predicted_category: str | None
    category_id: int | None
    confidence: float
    matched_keywords: list[str] = field(default_factory=list)
    probabilities: dict[str, float] = field(default_factory=dict)


@dataclass
class MatchedCategoryDetail:
    """
    Detailed metadata for an individual category matched during multi-category analysis.

    Fields:
        category_id: Database Category primary key.
        category_name: Title of category.
        match_count: Total count of domain keyword occurrences found.
        matched_keywords: Unique list of matched keyword tokens.
        confidence_score: Calculated confidence for this specific category match.
    """

    category_id: int
    category_name: str
    match_count: int
    matched_keywords: list[str]
    confidence_score: float


@dataclass
class MultiCategoryPredictionResult:
    """
    Overall result of multi-category classification returned to document upload handlers.

    Fields:
        is_fallback: True if document did not match any category keywords and fell back to 'Others'.
        categories: List of all matched category details.
        primary_category: Category with the highest keyword frequency / confidence.
        all_matched_keywords: Aggregated list of all matched keywords across all categories.
    """

    is_fallback: bool
    categories: list[MatchedCategoryDetail]
    primary_category: str
    all_matched_keywords: list[str]


# ==============================================================================
# Comprehensive Domain Corpus for Calibrated Base Training
# ==============================================================================

BASE_TRAINING_CORPUS: list[tuple[str, str]] = [
    # --- INVOICES ---
    (
        "Tax Invoice #INV-2024-0091 Bill to Acme Corp Ship to 123 Industrial Way Subtotal $4,500.00 "
        "VAT 18% Total Amount Due $5,310.00 Payment Terms Net 30 Due Date March 31 2024 Remittance wire transfer.",
        CategoryType.INVOICE.value,
    ),
    (
        "Commercial Invoice Quantity Unit Price Description Amount 50 units widget A $20.00 $1,000.00 "
        "Sales tax $80.00 Balance Due $1,080.00 Please remit payment to Bank Account #987654321.",
        CategoryType.INVOICE.value,
    ),
    (
        "Billing Statement Account Number 8472910 Previous Balance $250.00 New Charges $120.00 "
        "Total Payment Due by April 15. Thank you for your business. Purchase order PO-9921.",
        CategoryType.INVOICE.value,
    ),
    (
        "Receipt of Payment Customer Receipt Transaction ID #RC-84920 Date: 2024-01-15 "
        "Paid Amount: $450.00 Payment Method: Credit Card Subtotal Tax Total GST Paid in full.",
        CategoryType.INVOICE.value,
    ),
    (
        "Proforma Invoice Vendor: Global Logistics Ltd Client: Apex Retail PO Number: 4401 "
        "Line items itemized freight charges customs duties total amount payable remittance advice.",
        CategoryType.INVOICE.value,
    ),
    (
        "Monthly Invoice for Software Subscription Licenses 100 seats @ $15/user = $1,500.00 "
        "Discount applied $150 Net Amount Due $1,350.00 Payable to Cloud Solutions Inc.",
        CategoryType.INVOICE.value,
    ),
    (
        "Tax Invoice #INV-MED-7712 Bill to St. Jude Memorial Hospital Ship to Hospital Purchasing Dept "
        "Description 10x Surgical Scalpels Box $450.00 5x Stethoscopes $600.00 Subtotal $1,050.00 VAT 18% "
        "Total Amount Due $1,239.00 Payment Terms Net 30 wire transfer remittance bank transfer.",
        CategoryType.INVOICE.value,
    ),
    # --- CONTRACTS ---
    (
        "Non-Disclosure Agreement NDA This Agreement is entered into by and between the Disclosing Party "
        "and Receiving Party. The Receiving Party agrees to keep all Proprietary Information strictly confidential "
        "covenants non-compete governing law jurisdiction.",
        CategoryType.CONTRACTS.value,
    ),
    (
        "Master Services Agreement MSA between Client and Service Provider. Terms and conditions "
        "warranties indemnification limitation of liability intellectual property rights breach termination clause "
        "IN WITNESS WHEREOF the parties hereto have executed this Agreement.",
        CategoryType.CONTRACTS.value,
    ),
    (
        "Employment Contract Agreement made this 1st day of January between Employer and Employee. "
        "Compensation benefits confidentiality non-disclosure termination notice period signatory signatures "
        "severability and entire agreement clause.",
        CategoryType.CONTRACTS.value,
    ),
    (
        "Software License Agreement Grant of license restrictions warranty disclaimer indemnity "
        "breach of contract governing law State of California arbitration dispute resolution signed.",
        CategoryType.CONTRACTS.value,
    ),
    (
        "Commercial Lease Agreement Landlord and Tenant premises term monthly rent security deposit "
        "maintenance covenants default remedies signatories witnesseth.",
        CategoryType.CONTRACTS.value,
    ),
    (
        "Vendor Partnership Agreement Whereas both parties wish to collaborate under these contractual terms "
        "obligations liabilities confidentiality indemnity effective date signature of authorized officers.",
        CategoryType.CONTRACTS.value,
    ),
    (
        "Hospital Facilities Master Services Agreement between Metro General Hospital and CleanCare Facilities LLC. "
        "Terms and conditions warranties indemnification liability breach confidentiality termination clause "
        "governing law jurisdiction signatories witnesseth.",
        CategoryType.CONTRACTS.value,
    ),
    # --- REPORTS ---
    (
        "Quarterly Financial Report Q3 Executive Summary Revenue increased by 14% year over year. "
        "Key performance indicators KPI EBITDA operating margins market analysis findings and future outlook.",
        CategoryType.REPORTS.value,
    ),
    (
        "Annual Audit Report Independent Auditor's Report to the Board of Directors. "
        "Scope methodology assessment balance sheet evaluation internal controls conclusion and recommendations.",
        CategoryType.REPORTS.value,
    ),
    (
        "Market Research and Competitive Analysis Report Executive Overview Industry trends demographic breakdown "
        "consumer survey results data analysis benchmarks and strategic recommendations.",
        CategoryType.REPORTS.value,
    ),
    (
        "Project Status Progress Report Milestone achievements risk assessment schedule evaluation "
        "resource allocation metrics and completion deliverables summary.",
        CategoryType.REPORTS.value,
    ),
    (
        "Technical Evaluation Report System architecture performance benchmarks latency testing results "
        "findings conclusion and next phase recommendations.",
        CategoryType.REPORTS.value,
    ),
    (
        "Cybersecurity Risk Assessment Report Executive briefing vulnerability scanning findings "
        "threat analysis remediation roadmap and compliance audit evaluation.",
        CategoryType.REPORTS.value,
    ),
    (
        "Healthcare Industry Market Analysis Annual Report Executive Summary Global telemedicine adoption grew by 28%. "
        "Revenue growth EBITDA operating margin market trends competitive landscape and strategic recommendations for hospital networks.",
        CategoryType.REPORTS.value,
    ),
    # --- NOTES ---
    (
        "Meeting Minutes Team Standup Date 2024-02-10 Attendees Alice Bob Charlie. "
        "Agenda items discussed sprint roadmap backlog grooming. Action items: Alice to finish API Bob to review PR.",
        CategoryType.NOTES.value,
    ),
    (
        "Project Brainstorming Notes Quick ideas for new UI redesign dashboard layout user feedback summary "
        "to-do list follow-up with design team on Monday.",
        CategoryType.NOTES.value,
    ),
    (
        "Client Call Notes Discussion with John Doe regarding feature requirements. "
        "Key takeaways: needs CSV export by Friday. Next steps: send revised quote. Follow-up meeting scheduled.",
        CategoryType.NOTES.value,
    ),
    (
        "Internal Memo Subject: Q4 Strategy Session Summary. "
        "Key discussions action items assigned to engineering and marketing to-do follow-up reminder.",
        CategoryType.NOTES.value,
    ),
    (
        "Daily Scratchpad Notes Things to do today: fix database migration bug check logs review pull requests "
        "call vendor reminder quick note for tomorrow.",
        CategoryType.NOTES.value,
    ),
    (
        "Executive Briefing Notes Summary of leadership sync agenda points discussion topics "
        "decisions made next steps and action items.",
        CategoryType.NOTES.value,
    ),
    (
        "Clinic Staff Meeting Minutes Date 2024-03-12 Attendees Dr. Smith Dr. Davis Nurse Jones. "
        "Agenda items discussed shift scheduling EHR software update. Action items: Dr. Smith to finalize rota Nurse Jones to order clinic supplies.",
        CategoryType.NOTES.value,
    ),
    # --- MEDICAL ---
    (
        "Medical Prescription Doctor Rx Patient Name Jane Smith Age 38 Diagnosis Acute Bacterial Sinusitis "
        "Rx Amoxicillin Clavulanate 625mg 1 tablet orally twice daily after food for 7 days. Paracetamol 650mg SOS for fever and headache. "
        "Dosage directions take after meals drink plenty of fluids. Prescribed by Physician Dr. Robert Davis MD Clinic License #MD-88329.",
        CategoryType.MEDICAL.value,
    ),
    (
        "Hospital Inpatient Discharge Summary Patient Name John Williams Admission Date 2024-03-01 Discharge Date 2024-03-05 "
        "Department Internal Medicine Cardiology Final Diagnosis Acute Myocardial Infarction Post Coronary Angioplasty Stent Placement. "
        "Clinical course patient presented with chest pain underwent successful cardiac catheterization stable condition. "
        "Discharge medications Aspirin 81mg daily Atorvastatin 80mg Metoprolol 25mg. Follow-up consultation in outpatient cardiology clinic. Attending Physician Dr. Sarah Jenkins MD.",
        CategoryType.MEDICAL.value,
    ),
    (
        "Clinical Diagnostic Laboratory Pathology Report Patient Sample ID 99281 Complete Blood Count CBC Hemoglobin 13.8 g/dL "
        "Hematocrit 41% White Blood Cell Count WBC 6.8 x10^3/uL Platelet Count 240 x10^3/uL Serum Creatinine 0.9 mg/dL Fasting Blood Glucose 95 mg/dL "
        "Lipid Panel Total Cholesterol 180 mg/dL Reference Ranges normal clinical findings Pathologist Medical Laboratory Director Dr. Emily Vance MD.",
        CategoryType.MEDICAL.value,
    ),
    (
        "Radiology and Medical Diagnostic Imaging Report Examination MRI Lumbar Spine without contrast and CT Scan. "
        "Clinical History Lower back pain radiating to left leg radiculopathy. Findings No acute vertebral fracture normal alignment disc desiccation at L4-L5. "
        "Impression Mild lumbar spondylosis without severe spinal canal stenosis. Radiologist Dr. Michael Chang MD Department of Diagnostic Radiology.",
        CategoryType.MEDICAL.value,
    ),
    (
        "Medical Certificate of Sickness and Fitness This is to certify that patient Arthur Pendelton was examined at our medical clinic. "
        "Clinical diagnosis Acute Gastroenteritis with dehydration. The patient was administered IV fluids and prescribed oral rehydration therapy "
        "and antiemetic medication. The patient is medically unfit for duty and advised complete bed rest for 4 days. Medical Officer Dr. Linda Green MD Registration #MED-44912.",
        CategoryType.MEDICAL.value,
    ),
    (
        "Child and Adult Immunization Health Record Patient Medical Record Number MRN-82918 Vaccines Administered MMR Measles Mumps Rubella "
        "Dose 0.5mL intramuscular Hepatitis B Vaccine Tetanus Diphtheria Pertussis Tdap booster. Batch Number VAX-9941 Administration Site Left Deltoid. "
        "Adverse reaction none observed. Next vaccination due date pediatrician clinic visit.",
        CategoryType.MEDICAL.value,
    ),
    (
        "Surgical Pathology and Biopsy Report Specimen Left Thyroid Nodule Fine Needle Aspiration FNA Clinical History Solitary thyroid nodule. "
        "Microscopic examination shows benign follicular nodule colloid rich no cytological atypia or malignancy. Final Diagnosis Benign thyroid nodule "
        "Bethesda Category II Pathologist Dr. Karen Miller MD.",
        CategoryType.MEDICAL.value,
    ),
    (
        "Outpatient Clinical Consultation and Treatment Note Patient Chief Complaint Persistent dry cough and shortness of breath for 10 days. "
        "Physical Examination Vital Signs BP 120/80 mmHg Heart Rate 72 bpm Respiratory Rate 16 SpO2 98% on room air. Lungs clear to auscultation bilaterally. "
        "Assessment Viral Bronchitis. Plan Prescribed Albuterol inhaler and Guaifenesin syrup. Follow-up treatment in clinic if symptoms persist.",
        CategoryType.MEDICAL.value,
    ),
]


class DocumentCategorizer:
    """
    Production-grade ML Document Categorizer.
    Utilizes TF-IDF + Multinomial Naive Bayes combined with dynamic PostgreSQL
    `category_keyword` boosting for high accuracy and explainability.
    """

    def __init__(self):
        self.pipeline: Pipeline | None = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Trains and builds the initial in-memory TF-IDF + Naive Bayes classification pipeline."""
        try:
            texts = [item[0] for item in BASE_TRAINING_CORPUS]
            labels = [item[1] for item in BASE_TRAINING_CORPUS]

            self.pipeline = Pipeline(
                [
                    (
                        "tfidf",
                        TfidfVectorizer(
                            ngram_range=(1, 2),
                            lowercase=True,
                            stop_words="english",
                            sublinear_tf=True,
                            max_features=5000,
                        ),
                    ),
                    (
                        "clf",
                        MultinomialNB(alpha=0.1),
                    ),
                ]
            )

            self.pipeline.fit(texts, labels)
            logger.info("ML Document Categorizer initialized successfully.")
        except Exception as exc:
            logger.error(f"Failed to initialize ML Document Categorizer: {exc}")
            self.pipeline = None

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Cleans and normalizes input text for processing."""
        if not text:
            return ""
        # Lowercase and collapse multiple whitespace
        cleaned = re.sub(r"\s+", " ", text.lower().strip())
        return cleaned

    def _extract_category_keywords(
        self,
        normalized_text: str,
        session: Session | None,
    ) -> tuple[dict[int, int], dict[int, list[str]], dict[int, str]]:
        """
        Scans normalized text against reference keywords stored in the `category_keyword` table,
        with automated fallback to static category keyword definitions.
        Returns:
            - keyword_counts: Map of cat_id -> count of matched keyword hits
            - matched_words: Map of cat_id -> list of matched keyword strings
            - category_names: Map of cat_id -> category name
        """
        keyword_counts: dict[int, int] = {}
        matched_words: dict[int, list[str]] = {}
        category_names: dict[int, str] = {}

        if not normalized_text:
            return keyword_counts, matched_words, category_names

        keywords: Sequence[CategoryKeyword] = []
        if session:
            try:
                keywords = session.exec(select(CategoryKeyword)).all()
                categories = session.exec(select(Category)).all()
                category_names = {c.id: c.name for c in categories if c.id is not None}
            except Exception as exc:
                logger.warning(f"Error querying category_keyword: {exc}")

        # Fallback to static category keywords if database is empty or not yet seeded
        if not keywords:
            from src.data.database import STATIC_CATEGORY_KEYWORDS

            canonical_ids = {
                CategoryType.INVOICE.value: 1,
                CategoryType.CONTRACTS.value: 2,
                CategoryType.REPORTS.value: 3,
                CategoryType.NOTES.value: 4,
                CategoryType.MEDICAL.value: 5,
                CategoryType.OTHERS.value: 6,
            }
            category_names = {v: k for k, v in canonical_ids.items()}
            for cat_name, kw_list in STATIC_CATEGORY_KEYWORDS.items():
                cat_id = canonical_ids.get(cat_name, 6)
                for word in kw_list:
                    word_lower = word.strip().lower()
                    pattern = r"\b" + re.escape(word_lower) + r"\b"
                    matches = len(re.findall(pattern, normalized_text))
                    if matches > 0:
                        keyword_counts[cat_id] = keyword_counts.get(cat_id, 0) + matches
                        matched_words.setdefault(cat_id, []).append(word_lower)
            return keyword_counts, matched_words, category_names

        for kw in keywords:
            cat_id = kw.cat_id
            word = kw.keyword.strip().lower()
            pattern = r"\b" + re.escape(word) + r"\b"
            matches = len(re.findall(pattern, normalized_text))
            if matches > 0:
                keyword_counts[cat_id] = keyword_counts.get(cat_id, 0) + matches
                matched_words.setdefault(cat_id, []).append(word)

        return keyword_counts, matched_words, category_names

    def predict(
        self,
        text: str | None,
        session: Session | None = None,
    ) -> PredictionResult:
        """
        Predicts the document category from raw extracted OCR text.

        Pipeline Steps:
        1. Text Validation: Checks for empty or minimal text content.
        2. ML Inference: Obtains probability distribution across all 4 categories.
        3. Database Keyword Boosting: Queries `category_keyword` table for exact domain hits.
        4. Hybrid Scoring: Blends ML posterior probability with keyword density.
        5. Returns structured `PredictionResult` with category metadata & diagnostics.
        """
        if not text or len(text.strip()) < 10:
            return PredictionResult(
                predicted_category=None,
                category_id=None,
                confidence=0.0,
                matched_keywords=[],
                probabilities={},
            )

        normalized = self._normalize_text(text)

        # 1. Base ML Probabilities
        ml_probs: dict[str, float] = {}
        if self.pipeline:
            try:
                classes = list(self.pipeline.classes_)
                prob_values = self.pipeline.predict_proba([normalized])[0]
                ml_probs = {
                    cls_name: float(prob)
                    for cls_name, prob in zip(classes, prob_values, strict=False)
                }
            except Exception as exc:
                logger.warning(f"ML inference error: {exc}")

        # 2. Database Keyword Scan
        kw_counts, kw_matches, cat_id_to_name = self._extract_category_keywords(normalized, session)

        # 3. Hybrid Scoring (Combining ML Probabilities + Keyword Matches)
        total_kw_hits = sum(kw_counts.values())
        final_scores: dict[str, float] = {}
        num_classes = len(self.pipeline.classes_) if self.pipeline else 5
        default_prior = 1.0 / max(1, num_classes)

        for cat_enum in CategoryType:
            cat_name = cat_enum.value
            base_prob = ml_probs.get(
                cat_name,
                default_prior if cat_name != CategoryType.OTHERS.value else 0.0,
            )

            # Find matching cat_id for this category name
            matching_cat_ids = [
                cid for cid, cname in cat_id_to_name.items() if cname.lower() == cat_name.lower()
            ]
            cat_id = matching_cat_ids[0] if matching_cat_ids else None

            # Calculate keyword boost (normalized 0 to 1)
            kw_hits = kw_counts.get(cat_id, 0) if cat_id else 0
            kw_ratio = (kw_hits / total_kw_hits) if total_kw_hits > 0 else 0.0

            # Blended score: 60% ML model + 40% Keyword density (if keywords found)
            if total_kw_hits > 0:
                blended = (0.60 * base_prob) + (0.40 * kw_ratio)
            else:
                blended = base_prob

            final_scores[cat_name] = blended

        # 4. Determine Winner
        if not final_scores:
            return PredictionResult(
                predicted_category=None,
                category_id=None,
                confidence=0.0,
                matched_keywords=[],
                probabilities={},
            )

        winning_category = max(final_scores, key=lambda k: final_scores[k])
        confidence = final_scores[winning_category]

        # Resolve winning category ID and matched keywords
        winning_cat_id: int | None = None
        matched_keywords_list: list[str] = []

        for cid, cname in cat_id_to_name.items():
            if cname.lower() == winning_category.lower():
                winning_cat_id = cid
                matched_keywords_list = kw_matches.get(cid, [])[:MAX_MATCHED_KEYWORDS]
                break

        # Fallback if category_id wasn't in DB lookup map
        if winning_cat_id is None and session:
            try:
                db_cat = session.exec(
                    select(Category).where(Category.name == winning_category)
                ).first()
                if db_cat:
                    winning_cat_id = db_cat.id
            except Exception:
                pass

        # Check against minimum confidence threshold
        if confidence < ML_CONFIDENCE_THRESHOLD:
            logger.info(
                f"Prediction confidence {confidence:.2f} below threshold {ML_CONFIDENCE_THRESHOLD}"
            )

        return PredictionResult(
            predicted_category=winning_category,
            category_id=winning_cat_id,
            confidence=round(confidence, 4),
            matched_keywords=matched_keywords_list,
            probabilities={k: round(v, 4) for k, v in final_scores.items()},
        )

    def predict_multi(
        self,
        text: str | None,
        session: Session | None = None,
        min_keyword_hits: int = 1,
    ) -> MultiCategoryPredictionResult:
        """
        Determines all categories a document belongs to based on assigned keywords mapping.
        If no keywords match across categories, returns the 'Others' fallback category.
        """
        if not text or len(text.strip()) < 3:
            return self._get_fallback_result(session)

        normalized = self._normalize_text(text)
        kw_counts, kw_matches, cat_id_to_name = self._extract_category_keywords(normalized, session)

        matched_details: list[MatchedCategoryDetail] = []
        for cat_id, hits_count in kw_counts.items():
            if hits_count >= min_keyword_hits:
                cat_name = cat_id_to_name.get(cat_id, "Unknown")
                # Exclude 'Others' from keyword matching
                if cat_name.lower() in ("others", "general", "other", "misc"):
                    continue

                matched_words = list(dict.fromkeys(kw_matches.get(cat_id, [])))
                confidence = min(1.0, (hits_count * 0.15) + 0.40)
                matched_details.append(
                    MatchedCategoryDetail(
                        category_id=cat_id,
                        category_name=cat_name,
                        match_count=hits_count,
                        matched_keywords=matched_words,
                        confidence_score=round(confidence, 4),
                    )
                )

        # Sort descending by match count
        matched_details.sort(key=lambda x: x.match_count, reverse=True)

        if not matched_details:
            return self._get_fallback_result(session)

        all_keywords = [kw for d in matched_details for kw in d.matched_keywords]
        return MultiCategoryPredictionResult(
            is_fallback=False,
            categories=matched_details,
            primary_category=matched_details[0].category_name,
            all_matched_keywords=all_keywords,
        )

    def _get_fallback_result(self, session: Session | None) -> MultiCategoryPredictionResult:
        """Helper to resolve and return the 'Others' fallback category."""
        others_cat_id = 6
        if session:
            try:
                others_cat = session.exec(
                    select(Category).where(
                        func.lower(Category.name) == CategoryType.OTHERS.value.lower()
                    )
                ).first()
                if others_cat and others_cat.id:
                    others_cat_id = others_cat.id
            except Exception:
                pass

        return MultiCategoryPredictionResult(
            is_fallback=True,
            categories=[
                MatchedCategoryDetail(
                    category_id=others_cat_id,
                    category_name=CategoryType.OTHERS.value,
                    match_count=0,
                    matched_keywords=[],
                    confidence_score=1.0,
                )
            ],
            primary_category=CategoryType.OTHERS.value,
            all_matched_keywords=[],
        )


# ==============================================================================
# Module-level Singleton Instance
# ==============================================================================

_categorizer_instance: DocumentCategorizer | None = None


def get_categorizer() -> DocumentCategorizer:
    """Returns the singleton instance of DocumentCategorizer."""
    global _categorizer_instance
    if _categorizer_instance is None:
        _categorizer_instance = DocumentCategorizer()
    return _categorizer_instance


def predict_document_category(
    text: str | None,
    session: Session | None = None,
) -> PredictionResult:
    """
    Convenience functional facade for single-category document prediction.
    """
    categorizer = get_categorizer()
    return categorizer.predict(text=text, session=session)


def classify_document_multi_category(
    text: str | None,
    session: Session | None = None,
    min_keyword_hits: int = 1,
) -> MultiCategoryPredictionResult:
    """
    Convenience functional facade for multi-category document keyword classification.
    Checks all categories the document belongs to as per assigned keyword mappings.
    If no mapping is found, returns 'Others' / 'General'.
    """
    categorizer = get_categorizer()
    return categorizer.predict_multi(text=text, session=session, min_keyword_hits=min_keyword_hits)
