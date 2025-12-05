import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Contagem from './pages/Contagem';
import Exportacao from './pages/Exportacao';
import UserManagement from './pages/UserManagement';
import GestaoItens from './pages/GestaoItens';
import GestaoContagens from './pages/GestaoContagens';
import Dashboard from './pages/Dashboard';
import ProtectedRoute from './components/ProtectedRoute';
import { authService } from './services/api';
import './index.css';

const App = () => {
  // Função para determinar página inicial baseada na role
  const getDefaultRoute = () => {
    const user = authService.getCurrentUser();
    if (user && user.role === 'ADMIN') {
      return '/dashboard';
    }
    if (user && user.role === 'CONTROLADORIA') {
      return '/exportacao';
    }
    return '/contagem';
  };
  
  return (
    <BrowserRouter>
      <Routes>
        <Route 
          path="/" 
          element={
            authService.isAuthenticated() 
              ? <Navigate to={getDefaultRoute()} replace /> 
              : <Login />
          } 
        />
        
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/contagem" 
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'CONTADOR']}>
              <Contagem />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/itens" 
          element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <GestaoItens />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/gestao-contagens" 
          element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <GestaoContagens />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/exportacao" 
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'CONTROLADORIA']}>
              <Exportacao />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/usuarios" 
          element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <UserManagement />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="*" 
          element={<Navigate to="/" replace />} 
        />
      </Routes>
    </BrowserRouter>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
