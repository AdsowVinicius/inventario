import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Contagem from './pages/Contagem';
import Exportacao from './pages/Exportacao';
import ProtectedRoute from './components/ProtectedRoute';
import { authService } from './services/api';
import './index.css';

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route 
          path="/" 
          element={
            authService.isAuthenticated() 
              ? <Navigate to="/contagem" replace /> 
              : <Login />
          } 
        />
        
        <Route 
          path="/contagem" 
          element={
            <ProtectedRoute>
              <Contagem />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/exportacao" 
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'ENCARREGADO']}>
              <Exportacao />
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
