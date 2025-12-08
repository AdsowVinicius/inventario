import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { authService } from '../services/api';

const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const location = useLocation();
  const isAuthenticated = authService.isAuthenticated();
  const user = authService.getCurrentUser();
  
  // Se não está autenticado, redireciona para login
  if (!isAuthenticated || !user) {
    return <Navigate to="/" replace state={{ from: location }} />;
  }
  
  // Se é primeiro login e não está na página de alterar senha, redireciona
  if (user.primeiro_login && location.pathname !== '/alterar-senha') {
    return <Navigate to="/alterar-senha" replace />;
  }
  
  // Verificar papel do usuário se houver restrições
  if (allowedRoles.length > 0) {
    if (!allowedRoles.includes(user.role)) {
      // Redirecionar para página apropriada ao invés de mostrar erro
      if (user.role === 'ADMIN') {
        return <Navigate to="/dashboard" replace />;
      } else if (user.role === 'CONTROLADORIA') {
        return <Navigate to="/exportacao" replace />;
      } else {
        return <Navigate to="/contagem" replace />;
      }
    }
  }
  
  return children;
};

export default ProtectedRoute;
