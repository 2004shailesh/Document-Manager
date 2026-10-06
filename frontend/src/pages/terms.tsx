/**
 * ==============================================================================
 * Terms of Service Page Component
 * ==============================================================================
 * Author: Senior Software Engineer & Cloud Deployment Architect
 * Purpose:
 *   Specifies platform rules, acceptable use constraints, upload limits (3MB),
 *   intellectual property ownership, and service availability disclaimers.
 * ==============================================================================
 */

import { Link } from 'react-router-dom';
import './legal.css';

function TermsOfService() {
  const contactEmail = 'shaileshranjan9051@gmail.com';
  const effectiveDate = 'October 2026';

  return (
    <div className="legal-container">
      <div className="legal-card">
        <header className="legal-header">
          <span className="legal-badge">📜 Terms of Agreement</span>
          <h1>Terms of Service</h1>
          <p className="legal-updated">Effective Date: {effectiveDate}</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>
              <span className="section-num">1</span> Acceptance of Terms
            </h2>
            <p>
              By creating an account or accessing <strong>Document Manager</strong>, you agree to be bound by these
              Terms of Service and our Privacy Policy. If you do not agree to these terms, please do not use the application.
            </p>
          </section>

          <section className="legal-section">
            <h2>
              <span className="section-num">2</span> User Accounts & Authentication
            </h2>
            <p>
              When registering an account, you must provide accurate and verifiable information. You are solely
              responsible for maintaining the confidentiality of your account credentials and for all activities
              under your account.
            </p>
          </section>

          <section className="legal-section">
            <h2>
              <span className="section-num">3</span> Upload Constraints & Acceptable Use
            </h2>
            <p>To ensure fair platform usage, data integrity, and system stability, you agree to the following constraints:</p>
            <ul>
              <li>
                <strong>File Format & Size</strong>: Only valid PDF documents up to <strong>3 MB (3,145,728 bytes)</strong> in size may be uploaded.
              </li>
              <li>
                <strong>Prohibited Content</strong>: You must not upload documents containing malicious payloads, corrupted binaries, malware, or illegal material.
              </li>
              <li>
                <strong>Abuse Prevention</strong>: Automated scraping, denial-of-service attempts, or bypassing rate limits is strictly prohibited.
              </li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>
              <span className="section-num">4</span> Intellectual Property & Ownership
            </h2>
            <p>
              <strong>You retain 100% ownership</strong> of all files and content you upload to Document Manager. We claim no intellectual property rights over your documents.
            </p>
          </section>

          <section className="legal-section">
            <h2>
              <span className="section-num">5</span> OCR & Classification Accuracy
            </h2>
            <p>
              Text extraction (via RapidOCR / PyMuPDF) and automated document categorization are provided on an &quot;as-is&quot; basis. While our algorithms strive for high accuracy, we do not guarantee 100% optical character recognition precision on degraded or scanned documents.
            </p>
          </section>

          <section className="legal-section">
            <h2>
              <span className="section-num">6</span> Service Availability & Modifications
            </h2>
            <p>
              We continually improve Document Manager. We reserve the right to deploy updates, maintain infrastructure, or modify features with the goal of enhancing reliability and user experience.
            </p>
          </section>

          <div className="legal-contact-callout">
            <div>
              <h3>Legal Inquiries or Questions?</h3>
              <p>Direct inquiries to our administrator at <strong>{contactEmail}</strong></p>
            </div>
            <Link to="/contact" className="legal-contact-btn">
              ✉️ Contact Us
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TermsOfService;
