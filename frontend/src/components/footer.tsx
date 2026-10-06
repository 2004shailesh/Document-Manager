/**
 * ==============================================================================
 * Application Footer Component
 * ==============================================================================
 * Purpose:
 *   Universal footer displaying system copyright and legal/contact navigation links.
 * ==============================================================================
 */

import { Link } from 'react-router-dom';
import './footer.css';

function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <p>© {currentYear} Document Manager. All rights reserved.</p>
      <div className="footer-links">
        <Link to="/privacy" className="footer-link">
          Privacy Policy
        </Link>
        <Link to="/terms" className="footer-link">
          Terms of Service
        </Link>
        <Link to="/contact" className="footer-link">
          Contact
        </Link>
      </div>
    </footer>
  );
}

export default Footer;

