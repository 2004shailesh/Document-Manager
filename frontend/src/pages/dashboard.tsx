/**
 * ==============================================================================
 * Dashboard Page Component: Document Organization, Filtering & In-Memory Sorting
 * ==============================================================================
 * Purpose:
 *   Primary authenticated landing view. Displays category summary cards with
 *   per-category document counts and an interactive document list for selected categories.
 *
 * Architectural Flow:
 *   1. Authentication Guard: Reads cached user session from localStorage (`user`).
 *      Redirects to `/login` if unauthenticated.
 *   2. Data Ingestion:
 *      - Fetches user-specific documents from `GET /users/{userId}/documents`.
 *      - Fetches system categories from `GET /categories/`.
 *      - Aggregates document counts per category on the client.
 *   3. In-Memory Caching & Sorting (`useMemo`):
 *      - All user documents remain in memory (`userDocuments`).
 *      - Category selection and sorting happen instantly in client memory without
 *        triggering redundant backend queries.
 *      - Supports 4 sorting modes:
 *        1. `name_asc`: Name A → Z
 *        2. `name_desc`: Name Z → A
 *        3. `time_asc`: Old to New (earliest `uploaded_at` timestamp first)
 *        4. `time_desc`: New to Old (latest `uploaded_at` timestamp first)
 *   4. Direct BLOB Streaming Download:
 *      - Calls `GET /documents/{docId}/download`, converts binary response to a Blob URL,
 *        and triggers browser file download.
 * ==============================================================================
 */

import { useEffect, useState, useCallback, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import CategoryCard from '../components/categorycard';
import { getCategoryIcon } from '../utils/category';
import { API_BASE_URL } from '../utils/api';
import './dashboard.css';

interface UserProfile {
  id: number;
  name: string;
  email: string;
}

interface DashboardCategory {
  category: string;
  count: number;
}

interface UserDocumentItem {
  id: number;
  name: string;
  size_bytes: number;
  extracted_text?: string | null;
  uploaded_at?: string | null;
  category_ids?: number[];
  categories?: string[];
}

type SortOption = 'name_asc' | 'name_desc' | 'time_asc' | 'time_desc';

function Dashboard() {
  const [user] = useState<UserProfile | null>(() => {
    try {
      const stored = localStorage.getItem('user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });
  const [categories, setCategories] = useState<DashboardCategory[]>([]);
  const [userDocuments, setUserDocuments] = useState<UserDocumentItem[]>([]);
  const [categoryMap, setCategoryMap] = useState<Record<number, string>>({});
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [sortOption, setSortOption] = useState<SortOption>('name_asc');
  const [downloadingId, setDownloadingId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // 1. Verify user session
  useEffect(() => {
    if (!user) {
      navigate('/login');
    }
  }, [user, navigate]);

  // 2. Fetch user's documents and calculate user-specific category counts
  const fetchCategories = useCallback(async (userId: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/users/${userId}/documents`);
      if (!response.ok) {
        throw new Error(`Failed to fetch user documents (Status: ${response.status})`);
      }
      const userDocs: UserDocumentItem[] = await response.json();
      setUserDocuments(userDocs);

      const catResponse = await fetch(`${API_BASE_URL}/categories/`);
      const categoryList: Array<{ id: number; name: string }> = catResponse.ok
        ? await catResponse.json()
        : [
            { id: 1, name: 'Invoice' },
            { id: 2, name: 'Contracts' },
            { id: 3, name: 'Reports' },
            { id: 4, name: 'Notes' },
            { id: 5, name: 'Medical' },
            { id: 6, name: 'Others' },
          ];

      const categoryNameMap: Record<number, string> = {};
      categoryList.forEach((c) => {
        categoryNameMap[c.id] = c.name;
      });
      setCategoryMap(categoryNameMap);

      const countMap: Record<string, number> = {};
      categoryList.forEach((c) => {
        countMap[c.name] = 0;
      });

      userDocs.forEach((doc) => {
        if (Array.isArray(doc.category_ids) && doc.category_ids.length > 0) {
          doc.category_ids.forEach((catId) => {
            const name = categoryNameMap[catId] || `Category ${catId}`;
            countMap[name] = (countMap[name] || 0) + 1;
          });
        } else if (Array.isArray(doc.categories) && doc.categories.length > 0) {
          doc.categories.forEach((name) => {
            countMap[name] = (countMap[name] || 0) + 1;
          });
        } else {
          countMap['Others'] = (countMap['Others'] || 0) + 1;
        }
      });

      const allCategories: DashboardCategory[] = categoryList
        .map((c) => ({
          category: c.name,
          count: countMap[c.name] || 0,
        }))
        .sort((a, b) => b.count - a.count || a.category.localeCompare(b.category));

      setCategories(allCategories);
    } catch (err) {
      console.error('Dashboard categories fetch error:', err);
      setError(err instanceof Error ? err.message : 'Unable to load dashboard categories.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const userId = user?.id;
    if (!userId) return;

    let isMounted = true;
    const load = async () => {
      if (isMounted) {
        await fetchCategories(userId);
      }
    };
    void load();

    return () => {
      isMounted = false;
    };
  }, [user?.id, fetchCategories]);

  // Download original document binary file
  const handleDownload = async (docId: number, fileName: string) => {
    setDownloadingId(docId);
    try {
      const response = await fetch(`${API_BASE_URL}/documents/${docId}/download`);
      if (!response.ok) {
        throw new Error(`Download failed with status ${response.status}`);
      }
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = fileName || `document-${docId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      console.error('Download error:', err);
      alert('Failed to download document. Please ensure the backend server is running.');
    } finally {
      setDownloadingId(null);
    }
  };

  // Helper: Extract timestamp for chronological sorting (using existing database uploaded_at timestamp, fallback to ID)
  const getDocTimestamp = (doc: UserDocumentItem): number => {
    if (!doc.uploaded_at) return doc.id;
    const timeMs = new Date(doc.uploaded_at).getTime();
    return isNaN(timeMs) ? doc.id : timeMs;
  };

  // Helper: Format document timestamp for display
  const formatDocDate = (doc: UserDocumentItem): string | null => {
    if (!doc.uploaded_at) return null;
    try {
      const date = new Date(doc.uploaded_at);
      if (isNaN(date.getTime())) return null;
      return date.toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return null;
    }
  };

  // Filter and sort documents belonging to currently selected category (cached in memory)
  const sortedDocuments = useMemo(() => {
    if (!selectedCategory) return [];

    const normSelected = selectedCategory.toLowerCase().trim();
    const matched = userDocuments.filter((doc) => {
      if (Array.isArray(doc.category_ids) && doc.category_ids.length > 0) {
        const matchById = doc.category_ids.some((catId) => {
          const catName = (categoryMap[catId] || '').toLowerCase().trim();
          return catName === normSelected;
        });
        if (matchById) return true;
      }
      if (Array.isArray(doc.categories) && doc.categories.length > 0) {
        const matchByName = doc.categories.some(
          (c) => (c || '').toLowerCase().trim() === normSelected
        );
        if (matchByName) return true;
      }
      if (
        normSelected === 'others' &&
        (!doc.category_ids || doc.category_ids.length === 0) &&
        (!doc.categories || doc.categories.length === 0)
      ) {
        return true;
      }
      return false;
    });

    return [...matched].sort((a, b) => {
      switch (sortOption) {
        case 'name_desc':
          // 2. Name Z → A
          return b.name.localeCompare(a.name, undefined, { numeric: true, sensitivity: 'base' });
        case 'time_asc': {
          // 3. Old to New (earliest time first)
          const diff = getDocTimestamp(a) - getDocTimestamp(b);
          if (diff !== 0) return diff;
          return a.name.localeCompare(b.name, undefined, { numeric: true, sensitivity: 'base' });
        }
        case 'time_desc': {
          // 4. New to Old (latest time first)
          const diff = getDocTimestamp(b) - getDocTimestamp(a);
          if (diff !== 0) return diff;
          return a.name.localeCompare(b.name, undefined, { numeric: true, sensitivity: 'base' });
        }
        case 'name_asc':
        default:
          // 1. Name A → Z
          return a.name.localeCompare(b.name, undefined, { numeric: true, sensitivity: 'base' });
      }
    });
  }, [selectedCategory, userDocuments, categoryMap, sortOption]);

  if (!user) {
    return (
      <div className="dashboard">
        <section className="dashboard-content">
          <div className="dashboard-state loading-state" role="status">
            <div className="spinner" aria-hidden="true" />
            <p>Loading session...</p>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Header with User Info, CTA */}
      <section className="dashboard-header">
        <div>
          <h1>Welcome, {user.name}!</h1>
          <p>Manage, organize, and download your categorized documents.</p>
        </div>
      </section>

      {/* Main Content */}
      <section className="dashboard-content">
        {isLoading && (
          <div className="dashboard-state loading-state" role="status">
            <div className="spinner" aria-hidden="true" />
            <p>Loading document categories...</p>
          </div>
        )}

        {!isLoading && error && (
          <div className="dashboard-state error-state" role="alert">
            <div className="error-icon" aria-hidden="true">
              ⚠️
            </div>
            <div className="error-content">
              <h3>Unable to load categories</h3>
              <p>{error}</p>
              <button
                type="button"
                className="retry-button"
                onClick={() => user && fetchCategories(user.id)}
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {/* Empty State for New / 0-Document User */}
        {!isLoading && !error && userDocuments.length === 0 && (
          <div className="dashboard-state empty-state">
            <div className="empty-icon" aria-hidden="true">
              📂
            </div>
            <h3>OOPS ! upload a document</h3>
            <p>
              You haven't uploaded any documents yet. Upload a document to see your categorized
              document summaries here.
            </p>
            <Link to="/upload" className="empty-action-button">
              Upload your first document
            </Link>
          </div>
        )}

        {/* Category Cards Grid */}
        {!isLoading && !error && userDocuments.length > 0 && (
          <div className="categories-section">
            <div className="categories-section-header">
              <div>
                <h2>Document Categories</h2>
                <p className="section-subtitle">
                  Click any category below to view and download all its documents.
                </p>
              </div>
              {selectedCategory && (
                <button
                  type="button"
                  className="clear-filter-badge"
                  onClick={() => setSelectedCategory(null)}
                >
                  Showing: <strong>{selectedCategory}</strong> ✕
                </button>
              )}
            </div>

            <div className="category-grid">
              {categories.map((item) => (
                <CategoryCard
                  key={item.category}
                  name={item.category}
                  count={item.count}
                  isSelected={selectedCategory === item.category}
                  onClick={() => {
                    setSelectedCategory((prev) => (prev === item.category ? null : item.category));
                  }}
                />
              ))}
            </div>

            {/* Selected Category Documents List */}
            {selectedCategory && (
              <div className="category-documents-container">
                <div className="category-docs-header">
                  <div className="category-docs-title-group">
                    <span className="category-docs-icon">{getCategoryIcon(selectedCategory)}</span>
                    <div>
                      <h3>{selectedCategory} Documents</h3>
                      <p>
                        {sortedDocuments.length}{' '}
                        {sortedDocuments.length === 1 ? 'document' : 'documents'} available
                      </p>
                    </div>
                  </div>
                  <div className="category-docs-actions">
                    <div className="sort-control-group">
                      <label htmlFor="doc-sort-select" className="sort-label">
                        Sort by:
                      </label>
                      <select
                        id="doc-sort-select"
                        className="doc-sort-select"
                        value={sortOption}
                        onChange={(e) => setSortOption(e.target.value as SortOption)}
                        aria-label="Sort documents"
                      >
                        <option value="name_asc">Name A — Z</option>
                        <option value="name_desc">Name Z — A</option>
                        <option value="time_asc">Old to New</option>
                        <option value="time_desc">New to Old</option>
                      </select>
                    </div>
                    <button
                      type="button"
                      className="close-docs-btn"
                      onClick={() => setSelectedCategory(null)}
                    >
                      ✕ Close View
                    </button>
                  </div>
                </div>

                {sortedDocuments.length === 0 ? (
                  <div className="category-empty-docs">
                    <p>No documents found under {selectedCategory}.</p>
                  </div>
                ) : (
                  <div className="document-items-list">
                    {sortedDocuments.map((doc) => (
                      <div key={doc.id} className="document-item-card">
                        <div className="doc-icon-badge">📄</div>
                        <div className="doc-details-content">
                          <h4 className="doc-name-heading" title={doc.name}>
                            {doc.name}
                          </h4>
                          <div className="doc-meta-row">
                            <span className="doc-pill size-pill">
                              {(doc.size_bytes / 1024).toFixed(1)} KB
                            </span>
                            {formatDocDate(doc) && (
                              <span
                                className="doc-pill date-pill"
                                title={`Timestamp: ${new Date(doc.uploaded_at!).toLocaleString()}`}
                              >
                                🕒 {formatDocDate(doc)}
                              </span>
                            )}
                            {doc.categories && doc.categories.length > 0 ? (
                              doc.categories.map((catName) => (
                                <span
                                  key={catName}
                                  className="doc-pill category-pill"
                                  style={{
                                    background:
                                      catName.toLowerCase() === selectedCategory?.toLowerCase()
                                        ? '#dcfce7'
                                        : '#f1f5f9',
                                    color:
                                      catName.toLowerCase() === selectedCategory?.toLowerCase()
                                        ? '#166534'
                                        : '#475569',
                                    borderColor:
                                      catName.toLowerCase() === selectedCategory?.toLowerCase()
                                        ? '#bbf7d0'
                                        : '#e2e8f0',
                                  }}
                                >
                                  {catName}
                                </span>
                              ))
                            ) : doc.category_ids && doc.category_ids.length > 0 ? (
                              doc.category_ids.map((cid) => {
                                const catName = categoryMap[cid] || `Category ${cid}`;
                                return (
                                  <span
                                    key={cid}
                                    className="doc-pill category-pill"
                                    style={{
                                      background:
                                        catName.toLowerCase() === selectedCategory?.toLowerCase()
                                          ? '#dcfce7'
                                          : '#f1f5f9',
                                      color:
                                        catName.toLowerCase() === selectedCategory?.toLowerCase()
                                          ? '#166534'
                                          : '#475569',
                                      borderColor:
                                        catName.toLowerCase() === selectedCategory?.toLowerCase()
                                          ? '#bbf7d0'
                                          : '#e2e8f0',
                                    }}
                                  >
                                    {catName}
                                  </span>
                                );
                              })
                            ) : (
                              <span className="doc-pill category-pill">
                                {selectedCategory || 'Others'}
                              </span>
                            )}
                          </div>
                          {doc.extracted_text && (
                            <p className="doc-text-preview">
                              "{doc.extracted_text.slice(0, 140).trim()}
                              {doc.extracted_text.length > 140 ? '...' : ''}"
                            </p>
                          )}
                        </div>
                        <div className="doc-actions-wrapper">
                          <button
                            type="button"
                            className="doc-download-btn"
                            onClick={() => handleDownload(doc.id, doc.name)}
                            disabled={downloadingId === doc.id}
                            title={`Download ${doc.name}`}
                          >
                            {downloadingId === doc.id ? (
                              <>
                                <span className="btn-spinner" aria-hidden="true" />
                                Downloading...
                              </>
                            ) : (
                              <>
                                <span>📥</span> Download
                              </>
                            )}
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  );
}

export default Dashboard;
