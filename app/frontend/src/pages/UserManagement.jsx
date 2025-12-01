import React, { useState, useEffect } from 'react';
import { authService } from '../services/api';
import Navbar from '../components/Navbar';
import './UserManagement.css';

const PLANTAS = ['PS01', 'PS02', 'PS03', 'PS05', 'PS09', 'PB82'];
const ROLES = [
  { value: 'CONTADOR', label: 'Contador' },
  { value: 'ENCARREGADO', label: 'Encarregado' },
  { value: 'ADMIN', label: 'Administrador' }
];

const UserManagement = () => {
  const currentUser = authService.getCurrentUser();
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modoEdicao, setModoEdicao] = useState(false);
  const [usuarioEditando, setUsuarioEditando] = useState(null);
  
  const [formData, setFormData] = useState({
    user_name: '',
    senha: '',
    planta: currentUser.role === 'ENCARREGADO' ? currentUser.planta : 'PS01',
    role: 'CONTADOR'
  });

  useEffect(() => {
    carregarUsuarios();
  }, []);

  const carregarUsuarios = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/users/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUsuarios(data);
      } else if (response.status === 403) {
        setMessage({ type: 'error', text: 'Você não tem permissão para acessar esta página' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Erro ao carregar usuários' });
    } finally {
      setLoading(false);
    }
  };

  const abrirModalCriar = () => {
    setModoEdicao(false);
    setUsuarioEditando(null);
    setFormData({
      user_name: '',
      senha: '',
      planta: currentUser.role === 'ENCARREGADO' ? currentUser.planta : 'PS01',
      role: 'CONTADOR'
    });
    setShowModal(true);
  };

  const abrirModalEditar = (usuario) => {
    setModoEdicao(true);
    setUsuarioEditando(usuario);
    setFormData({
      user_name: usuario.user_name,
      senha: '',
      planta: usuario.planta,
      role: usuario.role
    });
    setShowModal(true);
  };

  const fecharModal = () => {
    setShowModal(false);
    setModoEdicao(false);
    setUsuarioEditando(null);
    setFormData({
      user_name: '',
      senha: '',
      planta: currentUser.role === 'ENCARREGADO' ? currentUser.planta : 'PS01',
      role: 'CONTADOR'
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const url = modoEdicao 
        ? `http://localhost:8000/users/${usuarioEditando.id}`
        : 'http://localhost:8000/users/';
      
      const method = modoEdicao ? 'PUT' : 'POST';
      
      // Se está editando e senha está vazia, não enviar senha
      const body = { ...formData };
      if (modoEdicao && !body.senha) {
        delete body.senha;
      }

      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(body)
      });

      if (response.ok) {
        setMessage({ 
          type: 'success', 
          text: modoEdicao ? 'Usuário atualizado com sucesso!' : 'Usuário criado com sucesso!' 
        });
        carregarUsuarios();
        fecharModal();
      } else {
        const data = await response.json();
        setMessage({ type: 'error', text: data.detail || 'Erro ao salvar usuário' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Erro ao salvar usuário' });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (usuario) => {
    if (!window.confirm(`Tem certeza que deseja deletar o usuário "${usuario.user_name}"?`)) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/users/${usuario.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Usuário deletado com sucesso!' });
        carregarUsuarios();
      } else {
        const data = await response.json();
        setMessage({ type: 'error', text: data.detail || 'Erro ao deletar usuário' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Erro ao deletar usuário' });
    } finally {
      setLoading(false);
    }
  };

  const getRoleLabel = (role) => {
    const roleObj = ROLES.find(r => r.value === role);
    return roleObj ? roleObj.label : role;
  };

  const podeEditarUsuario = (usuario) => {
    if (currentUser.role === 'ADMIN') return true;
    if (currentUser.role === 'ENCARREGADO') {
      return usuario.planta === currentUser.planta && usuario.role !== 'ADMIN';
    }
    return false;
  };

  return (
    <>
      <Navbar />
      <div className="user-management-container">
        <div className="user-management-header">
          <h1>Gestão de Usuários</h1>
          <button className="btn-criar" onClick={abrirModalCriar}>
            + Novo Usuário
          </button>
        </div>

        {message && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}

        {loading && <div className="loading">Carregando...</div>}

        <div className="usuarios-grid">
          <table className="usuarios-table">
            <thead>
              <tr>
                <th>Usuário</th>
                <th>Planta</th>
                <th>Perfil</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {usuarios.map(usuario => (
                <tr key={usuario.id}>
                  <td>{usuario.user_name}</td>
                  <td>{usuario.planta}</td>
                  <td>
                    <span className={`badge badge-${usuario.role.toLowerCase()}`}>
                      {getRoleLabel(usuario.role)}
                    </span>
                  </td>
                  <td>
                    {podeEditarUsuario(usuario) && (
                      <>
                        <button 
                          className="btn-editar"
                          onClick={() => abrirModalEditar(usuario)}
                        >
                          Editar
                        </button>
                        <button 
                          className="btn-deletar"
                          onClick={() => handleDelete(usuario)}
                          disabled={usuario.id === currentUser.id}
                        >
                          Deletar
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {showModal && (
          <div className="modal-overlay" onClick={fecharModal}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>{modoEdicao ? 'Editar Usuário' : 'Novo Usuário'}</h2>
                <button className="modal-close" onClick={fecharModal}>×</button>
              </div>

              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label>Nome de Usuário *</label>
                  <input
                    type="text"
                    value={formData.user_name}
                    onChange={(e) => setFormData({...formData, user_name: e.target.value})}
                    required
                    minLength={3}
                    placeholder="Digite o nome do usuário"
                  />
                </div>

                <div className="form-group">
                  <label>
                    Senha {modoEdicao ? '(deixe em branco para não alterar)' : '*'}
                  </label>
                  <input
                    type="password"
                    value={formData.senha}
                    onChange={(e) => setFormData({...formData, senha: e.target.value})}
                    required={!modoEdicao}
                    minLength={6}
                    placeholder={modoEdicao ? "Nova senha (opcional)" : "Digite a senha"}
                  />
                </div>

                <div className="form-group">
                  <label>Planta *</label>
                  <select
                    value={formData.planta}
                    onChange={(e) => setFormData({...formData, planta: e.target.value})}
                    required
                    disabled={currentUser.role === 'ENCARREGADO'}
                  >
                    {PLANTAS.map(planta => (
                      <option key={planta} value={planta}>{planta}</option>
                    ))}
                  </select>
                  {currentUser.role === 'ENCARREGADO' && (
                    <small className="help-text">
                      Você só pode criar usuários em sua planta ({currentUser.planta})
                    </small>
                  )}
                </div>

                <div className="form-group">
                  <label>Perfil *</label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({...formData, role: e.target.value})}
                    required
                  >
                    {ROLES.map(role => {
                      // ENCARREGADO não pode criar ADMIN
                      if (currentUser.role === 'ENCARREGADO' && role.value === 'ADMIN') {
                        return null;
                      }
                      return (
                        <option key={role.value} value={role.value}>
                          {role.label}
                        </option>
                      );
                    })}
                  </select>
                </div>

                <div className="modal-footer">
                  <button type="button" className="btn-cancelar" onClick={fecharModal}>
                    Cancelar
                  </button>
                  <button type="submit" className="btn-salvar" disabled={loading}>
                    {loading ? 'Salvando...' : 'Salvar'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default UserManagement;
