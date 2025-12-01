import React from 'react';
import { Navigate } from 'react-router-dom';
import { authService } from '../services/api';

const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const isAuthenticated = authService.isAuthenticated();
  const user = authService.getCurrentUser();
  
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  // Verificar papel do usuário se houver restrições
  if (allowedRoles.length > 0 && user) {
    if (!allowedRoles.includes(user.role)) {
      return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <h2>⚠️ Acesso Negado</h2>
          <p>Você não tem permissão para acessar esta página.</p>
          <button onClick={() => window.history.back()}>Voltar</button>
        </div>
      );
    }
  }
  
  return children;
};

export default ProtectedRoute;
