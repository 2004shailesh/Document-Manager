/**
 * ==============================================================================
 * Application Footer Component
 * ==============================================================================
 * Purpose:
 *   Universal footer displaying system copyright and legal/contact navigation links.
 * ==============================================================================
 */

import './footer.css';

function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <p>© {currentYear} Document Manager. All rights reserved.</p>
      <div className="footer-links">
        <a href="#" className="footer-link">
          Privacy Policy
        </a>
        <a href="#" className="footer-link">
          Terms of Service
        </a>
        <a href="#" className="footer-link">
          Contact
        </a>
      </div>
    </footer>
  );
}

export default Footer;
