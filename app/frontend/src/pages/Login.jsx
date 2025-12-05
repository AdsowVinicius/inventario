import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/api';
import './Login.css';

const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    user_name: '',
    senha: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await authService.login(formData.user_name, formData.senha);
      
      // Salvar token e usuário
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      
      // Redirecionar baseado na role
      if (response.user.role === 'ADMIN') {
        navigate('/dashboard');
      } else if (response.user.role === 'CONTROLADORIA') {
        navigate('/exportacao');
      } else {
        navigate('/contagem');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao fazer login. Verifique suas credenciais.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <img src="/logo.jpeg" alt="PSC" className="login-logo" />
          <h1>PSCInventário</h1>
          <p>Faça login para continuar</p>
        </div>
        
        <form onSubmit={handleSubmit} className="login-form">
          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}
          
          <div className="form-group">
            <label htmlFor="user_name">Usuário</label>
            <input
              type="text"
              id="user_name"
              name="user_name"
              value={formData.user_name}
              onChange={handleChange}
              placeholder="Digite seu usuário"
              required
              autoFocus
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="senha">Senha</label>
            <input
              type="password"
              id="senha"
              name="senha"
              value={formData.senha}
              onChange={handleChange}
              placeholder="Digite sua senha"
              required
            />
          </div>
          
          <button 
            type="submit" 
            className="btn-login"
            disabled={loading}
          >
            {loading ? '🔄 Entrando...' : '🚀 Entrar'}
          </button>
        </form>
        
        <div className="login-footer">
          <small>PSCInventário v1.0</small>
        </div>
      </div>
    </div>
  );
};

export default Login;
