import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/api';
import './Navbar.css';

const Navbar = () => {
  const navigate = useNavigate();
  const user = authService.getCurrentUser();
  
  const handleLogout = () => {
    authService.logout();
    navigate('/');
  };
  
  if (!user) return null;
  
  const canExport = user.role === 'ADMIN' || user.role === 'ENCARREGADO';
  const canManageUsers = user.role === 'ADMIN' || user.role === 'ENCARREGADO';
  
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <h1>📦 Sistema de Inventário</h1>
      </div>
      
      <div className="navbar-menu">
        <Link to="/contagem" className="navbar-item">
          📝 Contagem
        </Link>
        
        {canExport && (
          <Link to="/exportacao" className="navbar-item">
            📊 Exportação
          </Link>
        )}
        
        {canManageUsers && (
          <Link to="/usuarios" className="navbar-item">
            👥 Usuários
          </Link>
        )}
      </div>
      
      <div className="navbar-user">
        <span className="user-info">
          👤 {user.user_name} | {user.planta} | {user.role}
        </span>
        <button onClick={handleLogout} className="btn-logout">
          🚪 Sair
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
