import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/header';
import Footer from './components/footer';
import Login from './pages/login';
import Register from './pages/register';
import Dashboard from './pages/dashboard';
import Upload from './pages/upload';
import PrivacyPolicy from './pages/privacy';
import TermsOfService from './pages/terms';
import Contact from './pages/contact';

function App() {
  return (
    <BrowserRouter>
      {/* 1. Header renders at the top of every page */}
      <Header />

      {/* 2. Page content changes dynamically inside <Routes> */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <Routes>
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/privacy" element={<PrivacyPolicy />} />
          <Route path="/terms" element={<TermsOfService />} />
          <Route path="/contact" element={<Contact />} />

          {/* Default redirect to dashboard */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>

      {/* 3. Footer renders at the bottom of every page */}
      <Footer />
    </BrowserRouter>
  );
}

export default App;

