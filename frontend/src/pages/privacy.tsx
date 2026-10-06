/**
 * ==============================================================================
 * Privacy Policy Page Component
 * ==============================================================================
 * Author: Senior Software Engineer & Cloud Deployment Architect
 * Purpose:
 *   Transparently outlines user data handling, document storage privacy,
 *   OCR processing parameters, encryption standards, and contact details.
 * ==============================================================================
 */

import { Link } from 'react-router-dom';
import './legal.css';

function PrivacyPolicy() {
  const contactEmail = 'shaileshranjan9051@gmail.com';
  const effectiveDate = 'October 2026';

  return (
    <div className="legal-container">
      <div className="legal-card">
        <header className="legal-header">
          <span className="legal-badge">🔒 Legal & Compliance</span>
          <h1>Privacy Policy</h1>
          <p className="legal-updated">Last Updated & Effective: {effectiveDate}</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>
              <span className="section-num">1</span> Introduction & Overview
            </h2>
            <p>
              Welcome to <strong>Document Manager</strong>. Your privacy and the confidentiality of your documents
              are paramount. This Privacy Policy explains what information we collect, how it is processed and stored,
              and the security measures implemented to protect your personal and uploaded data.
            </p>
          </section>

          <section className="legal-section">
            <h2>
              <span className="section-num">2</span> Information We Collect
            </h2>
            <p>We collect only the minimum information necessary to provide our document classification and storage services:</p>
            <ul>
              <li>
                <strong>Account Credentials</strong>: Your full name, email address, and an encrypted hash of your password. We never store plain-text passwords.
              </li>
              <li>
                <strong>Uploaded Documents</strong>: PDF files (up to 3 MB each) that you choose to upload to the system.
              </li>
              <li>
                <strong>Extracted Text & Metadata</strong>: Text extracted via PyMuPDF/RapidOCR, file size, timestamps, and predicted category tags.
              </li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>
              <span className="section-num">3</span> How Your Data is Used
            </h2>
            <p>Your uploaded data is used solely to provide core platform functionality:</p>
            <ul>
              <li>Validating and categorizing uploaded documents using rule-based and ML keyword matching.</li>
              <li>Enabling you to search, sort, view, and download your stored documents.</li>
              <li>Authenticating your session and ensuring access isolation between users.</li>
            </ul>
            <div className="legal-highlight-box">
              <strong>🔒 Strict Data Isolation:</strong> Your documents are private to your user account. We do not sell, rent, or use your uploaded documents to train public third-party models.
            </div>
          </section>

          <section className="legal-section">
            <h2>
              <span className="section-num">4</span> Data Security & Architecture
            </h2>
            <p>We adopt industry-standard security architectures to safeguard your information:</p>
            <ul>
              <li>
                <strong>Cryptographic Hashing</strong>: Passwords are protected using robust Argon2/Bcrypt key-derivation hashing algorithms.
              </li>
              <li>
                <strong>Transport Layer Security (TLS)</strong>: All communication between your browser, Vercel frontend, and Render backend is encrypted with HTTPS/TLS.
              </li>
              <li>
                <strong>Database Persistence</strong>: Document binaries and extracted text are stored in secure PostgreSQL relational storage.
              </li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>
              <span className="section-num">5</span> User Rights & Data Deletion
            </h2>
            <p>
              You maintain full ownership of your data. You may request a complete export or permanent deletion of your user account and all associated documents at any time by contacting our administrator.
            </p>
          </section>

          <div className="legal-contact-callout">
            <div>
              <h3>Questions or Data Privacy Requests?</h3>
              <p>Contact our Data Protection administrator directly at <strong>{contactEmail}</strong></p>
            </div>
            <Link to="/contact" className="legal-contact-btn">
              ✉️ Contact Administrator
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PrivacyPolicy;
