import React, { useState, useEffect } from 'react';
import { authService } from '../services/api';
import Navbar from '../components/Navbar';
import './UserManagement.css';

const PLANTAS = ['PS01', 'PS02', 'PS03', 'PS05', 'PS09', 'PB82'];
const ROLES = [
  { value: 'CONTADOR', label: 'Contador' },
  { value: 'CONTROLADORIA', label: 'Controladoria' },
  { value: 'ADMIN', label: 'Administrador' }
];

const UserManagement = () => {
  const currentUser = authService.getCurrentUser();
  const [usuarios, setUsuarios] = useState([]);
  const [statusBloqueios, setStatusBloqueios] = useState({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modoEdicao, setModoEdicao] = useState(false);
  const [usuarioEditando, setUsuarioEditando] = useState(null);
  
  // Estados para pesquisa e filtro
  const [busca, setBusca] = useState('');
  const [filtroPlanta, setFiltroPlanta] = useState('');
  const [filtroRole, setFiltroRole] = useState('');
  
  const [formData, setFormData] = useState({
    user_name: '',
    email: '',
    nome_completo: '',
    departamento: '',
    senha: '',
    planta: currentUser.role === 'CONTROLADORIA' ? currentUser.planta : 'PS01',
    role: 'CONTADOR'
  });

  useEffect(() => {
    // Verificar se há token válido
    const token = localStorage.getItem('token');
    const user = authService.getCurrentUser();
    
    if (!token || !user) {
      window.location.href = '/';
      return;
    }
    
    carregarUsuarios();
    
    // Se for admin, carregar status de bloqueios e atualizar a cada 30 segundos
    if (currentUser.role === 'ADMIN') {
      carregarStatusBloqueios();
      const interval = setInterval(carregarStatusBloqueios, 30000);
      return () => clearInterval(interval);
    }
  }, []);

  const carregarStatusBloqueios = async () => {
    try {
      const response = await fetch('http://10.200.10.57:8000/auth/status-bloqueios-todos', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setStatusBloqueios(data);
      }
    } catch (error) {
      console.error('Erro ao carregar status de bloqueios:', error);
    }
  };

  const carregarUsuarios = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch('http://10.200.10.57:8000/users/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.status === 401) {
        // Token inválido ou expirado
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/';
        return;
      }

      if (response.ok) {
        const data = await response.json();
        setUsuarios(data);
      } else if (response.status === 403) {
        setMessage({ type: 'error', text: 'Você não tem permissão para acessar esta página' });
      } else {
        const errorData = await response.json().catch(() => ({}));
        setMessage({ type: 'error', text: errorData.detail || 'Erro ao carregar usuários' });
      }
    } catch (error) {
      console.error('Erro ao carregar usuários:', error);
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
      email: '',
      nome_completo: '',
      departamento: '',
      senha: '',
      planta: currentUser.role === 'CONTROLADORIA' ? currentUser.planta : 'PS01',
      role: 'CONTADOR'
    });
    setShowModal(true);
  };
  const abrirModalEditar = (usuario) => {
    setModoEdicao(true);
    setUsuarioEditando(usuario);
    setFormData({
      user_name: usuario.user_name,
      email: usuario.email || '',
      nome_completo: usuario.nome_completo || '',
      departamento: usuario.departamento || '',
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
      email: '',
      nome_completo: '',
      departamento: '',
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
        ? `http://10.200.10.57:8000/users/${usuarioEditando.id}`
        : 'http://10.200.10.57:8000/users/';
      
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

      if (response.status === 401) {
        // Token inválido ou expirado
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/';
        return;
      }

      if (response.ok) {
        setMessage({ 
          type: 'success', 
          text: modoEdicao ? 'Usuário atualizado com sucesso!' : 'Usuário criado com sucesso!' 
        });
        carregarUsuarios();
        fecharModal();
      } else {
        const data = await response.json().catch(() => ({}));
        setMessage({ type: 'error', text: data.detail || 'Erro ao salvar usuário' });
      }
    } catch (error) {
      console.error('Erro ao salvar usuário:', error);
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
    setMessage(null);
    try {
      const response = await fetch(`http://10.200.10.57:8000/users/${usuario.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.status === 401) {
        // Token inválido ou expirado
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/';
        return;
      }

      if (response.ok) {
        setMessage({ type: 'success', text: 'Usuário deletado com sucesso!' });
        carregarUsuarios();
      } else {
        const data = await response.json().catch(() => ({}));
        setMessage({ type: 'error', text: data.detail || 'Erro ao deletar usuário' });
      }
    } catch (error) {
      console.error('Erro ao deletar usuário:', error);
      setMessage({ type: 'error', text: 'Erro ao deletar usuário' });
    } finally {
      setLoading(false);
    }
  };

  const handleDesbloquear = async (usuario) => {
    if (!window.confirm(`Deseja desbloquear o usuário "${usuario.user_name}"?`)) {
      return;
    }

    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch(`http://10.200.10.57:8000/auth/desbloquear/${usuario.id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/';
        return;
      }

      if (response.ok) {
        setMessage({ type: 'success', text: `Usuário ${usuario.user_name} desbloqueado com sucesso!` });
        carregarUsuarios();
        carregarStatusBloqueios();
      } else {
        const data = await response.json().catch(() => ({}));
        setMessage({ type: 'error', text: data.detail || 'Erro ao desbloquear usuário' });
      }
    } catch (error) {
      console.error('Erro ao desbloquear usuário:', error);
      setMessage({ type: 'error', text: 'Erro ao desbloquear usuário' });
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

  // Função para filtrar usuários
  const usuariosFiltrados = usuarios.filter(usuario => {
    // Filtro por busca (nome, user_name, email, departamento)
    const termoBusca = busca.toLowerCase().trim();
    const matchBusca = !termoBusca || 
      usuario.user_name?.toLowerCase().includes(termoBusca) ||
      usuario.nome_completo?.toLowerCase().includes(termoBusca) ||
      usuario.email?.toLowerCase().includes(termoBusca) ||
      usuario.departamento?.toLowerCase().includes(termoBusca);
    
    // Filtro por planta
    const matchPlanta = !filtroPlanta || usuario.planta === filtroPlanta;
    
    // Filtro por role
    const matchRole = !filtroRole || usuario.role === filtroRole;
    
    return matchBusca && matchPlanta && matchRole;
  });

  const limparFiltros = () => {
    setBusca('');
    setFiltroPlanta('');
    setFiltroRole('');
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

        {/* Barra de Pesquisa e Filtros */}
        <div className="filtros-container">
          <div className="filtro-busca">
            <input
              type="text"
              placeholder="Pesquisar por nome, usuário, email ou departamento..."
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              className="input-busca"
            />
          </div>
          
          <div className="filtros-selects">
            <select
              value={filtroPlanta}
              onChange={(e) => setFiltroPlanta(e.target.value)}
              className="select-filtro"
            >
              <option value="">Todas as Plantas</option>
              {PLANTAS.map(planta => (
                <option key={planta} value={planta}>{planta}</option>
              ))}
            </select>
            
            <select
              value={filtroRole}
              onChange={(e) => setFiltroRole(e.target.value)}
              className="select-filtro"
            >
              <option value="">Todos os Perfis</option>
              {ROLES.map(role => (
                <option key={role.value} value={role.value}>{role.label}</option>
              ))}
            </select>
            
            {(busca || filtroPlanta || filtroRole) && (
              <button className="btn-limpar-filtros" onClick={limparFiltros}>
                Limpar Filtros
              </button>
            )}
          </div>
          
          <div className="filtros-info">
            <span>
              Exibindo {usuariosFiltrados.length} de {usuarios.length} usuários
            </span>
          </div>
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
                <th>Nome Completo</th>
                <th>Email</th>
                <th>Departamento</th>
                <th>Planta</th>
                <th>Perfil</th>
                <th>Status</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {usuariosFiltrados.length === 0 ? (
                <tr>
                  <td colSpan="8" className="no-results">
                    {usuarios.length === 0 
                      ? 'Nenhum usuário cadastrado'
                      : 'Nenhum usuário encontrado com os filtros aplicados'
                    }
                  </td>
                </tr>
              ) : (
                usuariosFiltrados.map(usuario => {
                  const statusBlq = statusBloqueios[usuario.user_name] || {};
                  const estaBloqueadoTemp = statusBlq.is_temporarily_locked;
                  const estaBloqueadoPerm = usuario.bloqueado_permanente;
                  const temTentativas = statusBlq.attempts > 0;
                  const tempoRestante = statusBlq.remaining_seconds || 0;
                  
                  // Formatar tempo restante
                  const formatarTempo = (segundos) => {
                    const min = Math.floor(segundos / 60);
                    const sec = segundos % 60;
                    return `${min}:${sec.toString().padStart(2, '0')}`;
                  };
                  
                  return (
                  <tr key={usuario.id} className={estaBloqueadoPerm || estaBloqueadoTemp ? 'usuario-bloqueado' : ''}>
                    <td>{usuario.user_name}</td>
                    <td>{usuario.nome_completo || '-'}</td>
                    <td>{usuario.email || '-'}</td>
                    <td>{usuario.departamento || '-'}</td>
                    <td>{usuario.planta}</td>
                    <td>
                      <span className={`badge badge-${usuario.role.toLowerCase()}`}>
                        {getRoleLabel(usuario.role)}
                      </span>
                    </td>
                    <td>
                      {estaBloqueadoPerm ? (
                        <span className="badge badge-bloqueado">Bloqueado Permanente</span>
                      ) : estaBloqueadoTemp ? (
                        <span className="badge badge-bloqueado-temp">
                          Bloqueado ({formatarTempo(tempoRestante)})
                        </span>
                      ) : temTentativas ? (
                        <span className="badge badge-alerta">
                          {statusBlq.remaining_attempts} tentativas
                        </span>
                      ) : (
                        <span className="badge badge-ativo">Ativo</span>
                      )}
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
                          {(estaBloqueadoPerm || estaBloqueadoTemp || temTentativas) && currentUser.role === 'ADMIN' && (
                            <button 
                              className="btn-desbloquear"
                              onClick={() => handleDesbloquear(usuario)}
                            >
                              Desbloquear
                            </button>
                          )}
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
                  );
                })
              )}
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
                  <label>Nome Completo *</label>
                  <input
                    type="text"
                    value={formData.nome_completo}
                    onChange={(e) => setFormData({...formData, nome_completo: e.target.value})}
                    required
                    minLength={3}
                    maxLength={60}
                    placeholder="Digite o nome completo"
                  />
                </div>

                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    placeholder="Digite o email do usuário"
                  />
                </div>

                <div className="form-group">
                  <label>Departamento *</label>
                  <input
                    type="text"
                    value={formData.departamento}
                    onChange={(e) => setFormData({...formData, departamento: e.target.value})}
                    required
                    minLength={2}
                    maxLength={60}
                    placeholder="Digite o departamento"
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
