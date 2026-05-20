import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, BookOpen, Sparkles, LogOut, FileText } from 'lucide-react';

function Layout({ children }) {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Get user details from localStorage
  const userString = localStorage.getItem('user');
  const user = userString ? JSON.parse(userString) : { nome: 'Usuário', email: 'user@user.com', cargo: 'user' };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const navItems = [
    { path: '/', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { path: '/storyteller', label: 'Storyteller IA', icon: <Sparkles size={20} /> },
    { path: '/lecture-extractor', label: 'Extrator de Aulas (TEC)', icon: <BookOpen size={20} /> },
  ];

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <Link to="/" className="brand">
          <div className="brand-icon">
            <Sparkles size={22} color="#fff" />
          </div>
          <span className="brand-name">Augenet AI</span>
        </Link>

        <nav style={{ flex: 1 }}>
          <ul className="nav-links">
            {navItems.map((item) => (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        {/* Sidebar Footer / User Profile */}
        <div className="sidebar-footer">
          <div className="user-profile">
            <div className="avatar">
              {user.nome ? user.nome.charAt(0).toUpperCase() : 'U'}
            </div>
            <div className="user-details">
              <span className="user-name">{user.nome || 'Usuário'}</span>
              <span className="user-role">{user.cargo || 'Membro'}</span>
            </div>
          </div>
          
          <button 
            type="button" 
            className="nav-item" 
            onClick={handleLogout} 
            style={{ width: '100%', border: 'none', background: 'transparent', textAlign: 'left', cursor: 'pointer' }}
          >
            <LogOut size={20} />
            <span>Sair da Conta</span>
          </button>
        </div>
      </aside>

      {/* Main Page Area */}
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}

export default Layout;
