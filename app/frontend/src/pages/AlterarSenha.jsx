import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/api';
import Navbar from '../components/Navbar';
import './AlterarSenha.css';

const AlterarSenha = () => {
  const navigate = useNavigate();
  const user = authService.getCurrentUser();
  const isPrimeiroLogin = user?.primeiro_login === true;
  
  const [formData, setFormData] = useState({
    senhaAtual: '',
    novaSenha: '',
    confirmarSenha: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showPasswords, setShowPasswords] = useState({
    atual: false,
    nova: false,
    confirmar: false
  });
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
    setSuccess('');
  };
  
  const toggleShowPassword = (field) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };
  
  const validarSenha = () => {
    if (!formData.senhaAtual) {
      setError('Digite sua senha atual');
      return false;
    }
    
    if (!formData.novaSenha) {
      setError('Digite a nova senha');
      return false;
    }
    
    if (formData.novaSenha.length < 6) {
      setError('A nova senha deve ter no mínimo 6 caracteres');
      return false;
    }
    
    if (formData.novaSenha !== formData.confirmarSenha) {
      setError('Nova senha e confirmação não coincidem');
      return false;
    }
    
    if (formData.senhaAtual === formData.novaSenha) {
      setError('A nova senha deve ser diferente da senha atual');
      return false;
    }
    
    return true;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validarSenha()) return;
    
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      await authService.alterarSenha(
        formData.senhaAtual,
        formData.novaSenha,
        formData.confirmarSenha
      );
      
      // Atualizar localStorage para marcar que não é mais primeiro login
      const updatedUser = { ...user, primeiro_login: false };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      
      setSuccess('Senha alterada com sucesso!');
      setFormData({
        senhaAtual: '',
        novaSenha: '',
        confirmarSenha: ''
      });
      
      // Redirecionar após 2 segundos
      setTimeout(() => {
        // Se era primeiro login, redirecionar para página correta
        if (isPrimeiroLogin) {
          if (updatedUser.role === 'ADMIN') {
            navigate('/dashboard');
          } else if (updatedUser.role === 'CONTROLADORIA') {
            navigate('/exportacao');
          } else {
            navigate('/contagem');
          }
        } else {
          navigate(-1); // Volta para página anterior
        }
      }, 2000);
      
    } catch (err) {
      const mensagem = err.response?.data?.detail || 'Erro ao alterar senha';
      setError(mensagem);
    } finally {
      setLoading(false);
    }
  };
  
  const handleVoltar = () => {
    // Se for primeiro login, não permitir voltar sem alterar a senha
    if (isPrimeiroLogin) {
      setError('Você precisa alterar sua senha antes de continuar');
      return;
    }
    navigate(-1);
  };
  
  return (
    <>
      <Navbar />
      <div className="alterar-senha-container">
        <div className="alterar-senha-card">
          <div className="alterar-senha-header">
            <h1>Alterar Senha</h1>
            <p>
              {isPrimeiroLogin 
                ? 'Para sua segurança, altere sua senha no primeiro acesso'
                : 'Altere sua senha de acesso ao sistema'
              }
            </p>
          </div>
          
          {isPrimeiroLogin && (
            <div className="alert alert-warning">
              Este é seu primeiro acesso. Por favor, crie uma nova senha pessoal.
            </div>
          )}
          
          <div className="user-info-box">
            <span className="user-icon-letter">{(user?.nome_completo || user?.user_name || 'U').charAt(0).toUpperCase()}</span>
            <div className="user-details">
              <strong>{user?.nome_completo || user?.user_name}</strong>
              <span>{user?.planta} | {user?.role}</span>
            </div>
          </div>
          
          {error && (
            <div className="alert alert-error">
              {error}
            </div>
          )}
          
          {success && (
            <div className="alert alert-success">
              {success}
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="alterar-senha-form">
            <div className="form-group">
              <label htmlFor="senhaAtual">Senha Atual *</label>
              <div className="password-input-wrapper">
                <input
                  type={showPasswords.atual ? 'text' : 'password'}
                  id="senhaAtual"
                  name="senhaAtual"
                  value={formData.senhaAtual}
                  onChange={handleChange}
                  placeholder="Digite sua senha atual"
                  required
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  className="toggle-password"
                  onClick={() => toggleShowPassword('atual')}
                  tabIndex={-1}
                >
                  {showPasswords.atual ? 'Ocultar' : 'Ver'}
                </button>
              </div>
            </div>
            
            <div className="form-group">
              <label htmlFor="novaSenha">Nova Senha *</label>
              <div className="password-input-wrapper">
                <input
                  type={showPasswords.nova ? 'text' : 'password'}
                  id="novaSenha"
                  name="novaSenha"
                  value={formData.novaSenha}
                  onChange={handleChange}
                  placeholder="Digite a nova senha (mín. 6 caracteres)"
                  required
                  minLength={6}
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  className="toggle-password"
                  onClick={() => toggleShowPassword('nova')}
                  tabIndex={-1}
                >
                  {showPasswords.nova ? 'Ocultar' : 'Ver'}
                </button>
              </div>
              <small className="form-hint">Mínimo de 6 caracteres</small>
            </div>
            
            <div className="form-group">
              <label htmlFor="confirmarSenha">Confirmar Nova Senha *</label>
              <div className="password-input-wrapper">
                <input
                  type={showPasswords.confirmar ? 'text' : 'password'}
                  id="confirmarSenha"
                  name="confirmarSenha"
                  value={formData.confirmarSenha}
                  onChange={handleChange}
                  placeholder="Confirme a nova senha"
                  required
                  minLength={6}
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  className="toggle-password"
                  onClick={() => toggleShowPassword('confirmar')}
                  tabIndex={-1}
                >
                  {showPasswords.confirmar ? 'Ocultar' : 'Ver'}
                </button>
              </div>
            </div>
            
            <div className="form-actions">
              {!isPrimeiroLogin && (
                <button
                  type="button"
                  className="btn-cancelar"
                  onClick={handleVoltar}
                  disabled={loading}
                >
                  Voltar
                </button>
              )}
              <button
                type="submit"
                className={`btn-alterar ${isPrimeiroLogin ? 'btn-full-width' : ''}`}
                disabled={loading}
              >
                {loading ? 'Alterando...' : 'Alterar Senha'}
              </button>
            </div>
          </form>
          
          <div className="senha-dicas">
            <h4>Dicas para uma senha segura:</h4>
            <ul>
              <li>Use pelo menos 6 caracteres</li>
              <li>Combine letras maiúsculas e minúsculas</li>
              <li>Inclua números e símbolos</li>
              <li>Evite informações pessoais</li>
            </ul>
          </div>
        </div>
      </div>
    </>
  );
};

export default AlterarSenha;
