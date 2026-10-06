/**
 * ==============================================================================
 * Contact & Support Page Component
 * ==============================================================================
 * Author: Senior Software Engineer & Cloud Deployment Architect
 * Purpose:
 *   Provides developer and administrator contact channels, inquiry composition,
 *   system status metrics, and direct email communication utilities.
 * ==============================================================================
 */

import { useState } from 'react';
import './contact.css';

function Contact() {
  const contactEmail = 'shaileshranjan9051@gmail.com';
  const [copied, setCopied] = useState(false);
  const [subject, setSubject] = useState('');
  const [category, setCategory] = useState('Support');
  const [senderName, setSenderName] = useState('');
  const [message, setMessage] = useState('');

  const handleCopyEmail = async () => {
    try {
      await navigator.clipboard.writeText(contactEmail);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // Fallback if clipboard API not available
      const textarea = document.createElement('textarea');
      textarea.value = contactEmail;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  const handleSendEmail = (e: React.FormEvent) => {
    e.preventDefault();
    const mailtoSubject = encodeURIComponent(`[Document Manager - ${category}] ${subject}`);
    const mailtoBody = encodeURIComponent(
      `Hello Shailesh,\n\n${message}\n\n---\nSent by: ${senderName || 'Anonymous'}`
    );
    window.location.href = `mailto:${contactEmail}?subject=${mailtoSubject}&body=${mailtoBody}`;
  };

  return (
    <div className="contact-container">
      <header className="contact-header">
        <span className="contact-badge">💬 Support & Inquiries</span>
        <h1>Get in Touch</h1>
        <p>Have questions, feedback, or need technical assistance? Contact the developer directly.</p>
      </header>

      <div className="contact-grid">
        {/* Left Card: Direct Contact & Spec Info */}
        <div className="contact-card">
          <div className="contact-info-list">
            <div className="contact-info-item">
              <div className="contact-icon-box">✉️</div>
              <div className="contact-info-details">
                <h3>Direct Email</h3>
                <a href={`mailto:${contactEmail}`} className="contact-email-text">
                  {contactEmail}
                </a>
                <div className="contact-action-buttons">
                  <button type="button" className="btn-copy" onClick={handleCopyEmail}>
                    📋 {copied ? 'Copied!' : 'Copy Email'}
                  </button>
                  <a href={`mailto:${contactEmail}`} className="btn-email">
                    🚀 Open Mail App
                  </a>
                </div>
                {copied && <span className="copy-toast">✓ Copied to clipboard!</span>}
              </div>
            </div>

            <div className="contact-info-item">
              <div className="contact-icon-box">⚡</div>
              <div className="contact-info-details">
                <h3>Typical Response Time</h3>
                <p>Replies within 24–48 hours for general inquiries and technical support.</p>
              </div>
            </div>

            <div className="contact-info-item">
              <div className="contact-icon-box">📂</div>
              <div className="contact-info-details">
                <h3>Source Repository</h3>
                <a
                  href="https://github.com/2004shailesh/Document-Manager"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="contact-email-text"
                >
                  GitHub: 2004shailesh/Document-Manager
                </a>
              </div>
            </div>
          </div>

          <div className="contact-spec-box">
            <h4>System Specifications</h4>
            <ul className="contact-spec-list">
              <li>
                <span className="contact-spec-label">Service SLA:</span>
                <span className="contact-spec-val">24/7 Available</span>
              </li>
              <li>
                <span className="contact-spec-label">Max File Size:</span>
                <span className="contact-spec-val">3 MB per PDF</span>
              </li>
              <li>
                <span className="contact-spec-label">Extraction Engine:</span>
                <span className="contact-spec-val">RapidOCR + PyMuPDF</span>
              </li>
              <li>
                <span className="contact-spec-label">Database:</span>
                <span className="contact-spec-val">PostgreSQL</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Right Card: Inquiry Form */}
        <div className="contact-card">
          <form className="contact-form" onSubmit={handleSendEmail}>
            <div>
              <h2>Send an Inquiry</h2>
              <p className="contact-form-subtitle">
                Compose your message below. Submitting will open your default email app with pre-filled details.
              </p>
            </div>

            <div className="contact-form-group">
              <label htmlFor="name">Your Name</label>
              <input
                id="name"
                type="text"
                placeholder="e.g. Alex Smith"
                value={senderName}
                onChange={(e) => setSenderName(e.target.value)}
                required
              />
            </div>

            <div className="contact-form-group">
              <label htmlFor="category">Inquiry Type</label>
              <select
                id="category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                <option value="Support">Technical Support & Troubleshooting</option>
                <option value="Feature Request">Feature Request / Feedback</option>
                <option value="Bug Report">Bug Report</option>
                <option value="Account Deletion">Account / Data Deletion Request</option>
                <option value="General">General Question</option>
              </select>
            </div>

            <div className="contact-form-group">
              <label htmlFor="subject">Subject</label>
              <input
                id="subject"
                type="text"
                placeholder="Brief summary of your inquiry"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                required
              />
            </div>

            <div className="contact-form-group">
              <label htmlFor="message">Message</label>
              <textarea
                id="message"
                placeholder="Please describe your question or issue in detail..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                required
              ></textarea>
            </div>

            <button type="submit" className="contact-submit-btn">
              ✉️ Compose & Send Message
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Contact;
