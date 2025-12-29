import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import './Header.css';

export default function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="app-header">
      <div className="header-content">
        <Link to="/designer" className="header-logo">
          <span className="logo-icon">⚔️</span>
          <span className="logo-text">Raveling</span>
        </Link>
        
        <nav className="header-nav">
          <Link to="/about" className="nav-link">About</Link>
          <Link to="/gameplay" className="nav-link">Gameplay</Link>
          <Link to="/designer" className="nav-link">Designer Suite</Link>
          {user?.role === 'admin' && (
            <Link to="/admin/users" className="nav-link admin-link">Admin</Link>
          )}
        </nav>

        {user && (
          <div className="header-user">
            <span className="user-name">{user.username}</span>
            <span className="user-role">[{user.role}]</span>
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  );
}

