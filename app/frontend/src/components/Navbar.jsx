import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { authService } from '../services/api';
import './Navbar.css';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const user = authService.getCurrentUser();
  const [menuAberto, setMenuAberto] = useState(false);
  
  const handleLogout = () => {
    authService.logout();
    navigate('/');
  };
  
  const fecharMenu = () => {
    setMenuAberto(false);
  };
  
  const toggleMenu = () => {
    setMenuAberto(!menuAberto);
  };
  
  if (!user) return null;
  
  const canCount = user.role === 'ADMIN' || user.role === 'CONTADOR';
  const canExport = user.role === 'ADMIN' || user.role === 'CONTROLADORIA';
  const canManageUsers = user.role === 'ADMIN';
  const canManageItens = user.role === 'ADMIN';
  const canManageContagens = user.role === 'ADMIN';
  const canViewDashboard = user.role === 'ADMIN';
  
  const isActive = (path) => location.pathname === path;
  
  return (
    <nav className="navbar">
      <div className="navbar-main">
        <div className="navbar-brand">
          <img src="/logo.jpeg" alt="PSC" className="navbar-logo" />
          <h1>PSCInventário</h1>
        </div>
        
        {/* Botão Hamburger - Mobile */}
        <button 
          className={`hamburger ${menuAberto ? 'active' : ''}`}
          onClick={toggleMenu}
          aria-label="Menu"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
        
        {/* Menu Desktop */}
        <div className="navbar-desktop">
          <div className="navbar-menu">
            {canViewDashboard && (
              <Link to="/dashboard" className={`navbar-item ${isActive('/dashboard') ? 'active' : ''}`}>
                📊 Dashboard
              </Link>
            )}
            
            {canCount && (
              <Link to="/contagem" className={`navbar-item ${isActive('/contagem') ? 'active' : ''}`}>
                📝 Contagem
              </Link>
            )}
            
            {canManageContagens && (
              <Link to="/gestao-contagens" className={`navbar-item ${isActive('/gestao-contagens') ? 'active' : ''}`}>
                📋 Gestão
              </Link>
            )}
            
            {canManageItens && (
              <Link to="/itens" className={`navbar-item ${isActive('/itens') ? 'active' : ''}`}>
                📦 Itens
              </Link>
            )}
            
            {canExport && (
              <Link to="/exportacao" className={`navbar-item ${isActive('/exportacao') ? 'active' : ''}`}>
                📤 Exportação
              </Link>
            )}
            
            {canManageUsers && (
              <Link to="/usuarios" className={`navbar-item ${isActive('/usuarios') ? 'active' : ''}`}>
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
        </div>
      </div>
      
      {/* Menu Mobile */}
      <div className={`navbar-mobile ${menuAberto ? 'open' : ''}`}>
        <div className="mobile-user-info">
          👤 {user.user_name} | {user.planta} | {user.role}
        </div>
        
        <div className="mobile-menu">
          {canViewDashboard && (
            <Link 
              to="/dashboard" 
              className={`mobile-item ${isActive('/dashboard') ? 'active' : ''}`}
              onClick={fecharMenu}
            >
              📊 Dashboard
            </Link>
          )}
          
          {canCount && (
            <Link 
              to="/contagem" 
              className={`mobile-item ${isActive('/contagem') ? 'active' : ''}`}
              onClick={fecharMenu}
            >
              📝 Contagem
            </Link>
          )}
          
          {canManageContagens && (
            <Link 
              to="/gestao-contagens" 
              className={`mobile-item ${isActive('/gestao-contagens') ? 'active' : ''}`}
              onClick={fecharMenu}
            >
              📋 Gestão de Contagens
            </Link>
          )}
          
          {canManageItens && (
            <Link 
              to="/itens" 
              className={`mobile-item ${isActive('/itens') ? 'active' : ''}`}
              onClick={fecharMenu}
            >
              📦 Gestão de Itens
            </Link>
          )}
          
          {canExport && (
            <Link 
              to="/exportacao" 
              className={`mobile-item ${isActive('/exportacao') ? 'active' : ''}`}
              onClick={fecharMenu}
            >
              📤 Exportação
            </Link>
          )}
          
          {canManageUsers && (
            <Link 
              to="/usuarios" 
              className={`mobile-item ${isActive('/usuarios') ? 'active' : ''}`}
              onClick={fecharMenu}
            >
              👥 Usuários
            </Link>
          )}
        </div>
        
        <button onClick={handleLogout} className="mobile-logout">
          🚪 Sair do Sistema
        </button>
      </div>
      
      {/* Overlay para fechar menu */}
      {menuAberto && <div className="navbar-overlay" onClick={fecharMenu}></div>}
    </nav>
  );
};

export default Navbar;
