/**
 * ==============================================================================
 * Document Upload Page Component
 * ==============================================================================
 * Purpose:
 *   Handles client-side PDF selection, size pre-validation (<= 3MB), multipart/form-data
 *   submission to `POST /documents/`, and rendering of real-time classification results.
 *
 * Ingestion Flow:
 *   1. File Selection: Restricts input to `.pdf` files.
 *   2. Client Validation: Immediately rejects files > 3 MB with clear feedback.
 *   3. Multipart Upload: Sends binary payload and `owner_user_id` to the backend.
 *   4. Backend Processing:
 *      - Defense-in-depth PDF signature check.
 *      - Text extraction via PyMuPDF or RapidOCR fallback.
 *      - Multi-category keyword classification.
 *      - PostgreSQL BYTEA persistence.
 *   5. Response & Diagnostics: Displays assigned categories, confidence scores,
 *      and direct navigation link back to the Dashboard.
 * ==============================================================================
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { API_BASE_URL } from '../utils/api';
import './upload.css';

interface CategorySummary {
  id: number;
  name: string;
}

interface DocumentUploadResponse {
  id: number;
  name: string;
  size_bytes: number;
  extracted_text: string | null;
  owner_user_id: number | null;
  categories: CategorySummary[];
  predicted_category: string | null;
  prediction_confidence: number | null;
  matched_keywords: string[];
}

const MAX_FILE_SIZE_MB = 3;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024; // 3 MB (3,145,728 bytes)

function Upload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<DocumentUploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const formatFileSize = (bytes: number): string => {
    if (bytes >= 1024 * 1024) {
      return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
    }
    return `${(bytes / 1024).toFixed(1)} KB`;
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a PDF file to upload.');
      return;
    }

    if (selectedFile.size > MAX_FILE_SIZE_BYTES) {
      setError(
        `File size (${formatFileSize(selectedFile.size)}) exceeds the maximum allowed limit of ${MAX_FILE_SIZE_MB} MB. Please select a file smaller than or equal to ${MAX_FILE_SIZE_MB} MB.`
      );
      return;
    }

    setError(null);
    setIsUploading(true);

    const formdata = new FormData();
    formdata.append('file', selectedFile);

    const user = JSON.parse(localStorage.getItem('user') || 'null');
    if (user?.id) {
      formdata.append('owner_user_id', user.id.toString());
    }

    try {
      const response = await fetch(`${API_BASE_URL}/documents/`, {
        method: 'POST',
        body: formdata,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Document upload failed.');
      }

      console.log('Upload Successful', data);
      setUploadResult(data);
      setSelectedFile(null);
    } catch (err) {
      console.error('Upload error:', err);
      setError(
        err instanceof Error ? err.message : 'Upload failed. Please check backend connection.'
      );
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="upload-page">
      <div className="upload-container">
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '24px',
          }}
        >
          <h1 className="page-title" style={{ margin: 0 }}>
            Document Upload
          </h1>
          <Link
            to="/dashboard"
            style={{ textDecoration: 'none', color: '#2563eb', fontWeight: 600, fontSize: '14px' }}
          >
            ← Back to Dashboard
          </Link>
        </div>

        {/* Upload Section */}
        <div className="section">
          <h2 className="section-title">Upload & Classify Document</h2>
          <p style={{ color: '#6b7280', fontSize: '14px', marginTop: 0, marginBottom: '20px' }}>
            Upload a PDF document (max {MAX_FILE_SIZE_MB} MB). The system will extract text,
            classify the content, and add it to your dashboard categories.
          </p>

          {error && (
            <div
              style={{
                background: '#fef2f2',
                border: '1px solid #fecaca',
                color: '#b91c1c',
                padding: '12px 16px',
                borderRadius: '8px',
                marginBottom: '16px',
                fontSize: '14px',
              }}
            >
              ⚠️ {error}
            </div>
          )}

          <input
            className="file-input"
            type="file"
            accept=".pdf"
            disabled={isUploading}
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) {
                if (file.size > MAX_FILE_SIZE_BYTES) {
                  setError(
                    `File "${file.name}" is ${formatFileSize(file.size)}, which exceeds the maximum allowed limit of ${MAX_FILE_SIZE_MB} MB. Please upload a file less than or equal to ${MAX_FILE_SIZE_MB} MB.`
                  );
                  setSelectedFile(null);
                  event.target.value = '';
                  setUploadResult(null);
                  return;
                }
              }
              setSelectedFile(file || null);
              setError(null);
              setUploadResult(null);
            }}
          />

          {selectedFile && (
            <p className="selected-file">
              Selected file: <strong>{selectedFile.name}</strong> (
              {formatFileSize(selectedFile.size)})
            </p>
          )}

          <button
            className="upload-button"
            onClick={handleUpload}
            disabled={isUploading || !selectedFile}
            style={{
              opacity: isUploading || !selectedFile ? 0.6 : 1,
              cursor: isUploading || !selectedFile ? 'not-allowed' : 'pointer',
            }}
          >
            {isUploading ? 'Extracting & Classifying...' : 'Upload Document'}
          </button>

          {uploadResult && (
            <div className="success-card">
              <h2 className="success-title">✓ Upload & Classification Successful</h2>

              <p>
                <strong>Document Name:</strong> {uploadResult.name}
              </p>

              <div>
                <strong>Assigned Categories:</strong>
                <div
                  style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '8px',
                    marginTop: '8px',
                    marginBottom: '16px',
                  }}
                >
                  {uploadResult.categories && uploadResult.categories.length > 0 ? (
                    uploadResult.categories.map((cat) => (
                      <span
                        key={cat.id}
                        className="category-pill-badge"
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          background: '#dcfce7',
                          color: '#166534',
                          border: '1px solid #bbf7d0',
                          padding: '4px 10px',
                          borderRadius: '9999px',
                          fontWeight: 600,
                          fontSize: '13px',
                        }}
                      >
                        📁 {cat.name}
                      </span>
                    ))
                  ) : (
                    <span
                      className="category-pill-badge"
                      style={{
                        background: '#dcfce7',
                        color: '#166534',
                        padding: '4px 10px',
                        borderRadius: '9999px',
                        fontWeight: 600,
                        fontSize: '13px',
                      }}
                    >
                      {uploadResult.predicted_category ?? 'Others'}
                    </span>
                  )}
                </div>
              </div>

              <div style={{ marginTop: '18px' }}>
                <Link
                  to="/dashboard"
                  style={{
                    display: 'inline-block',
                    padding: '9px 18px',
                    background: '#16a34a',
                    color: '#ffffff',
                    borderRadius: '6px',
                    textDecoration: 'none',
                    fontWeight: 600,
                    fontSize: '14px',
                  }}
                >
                  View in Dashboard →
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Upload;
