function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h2>DocClassify</h2>
      </div>

      <nav className="sidebar-nav">
        <ul>
          <li>Dashboard</li>
          <li>Documents</li>
          <li>Categories</li>
          <li>Settings</li>
        </ul>
      </nav>
    </aside>
  );
}

export default Sidebar;
