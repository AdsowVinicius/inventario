import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { authService } from '../services/api';
import api from '../services/api';
import './GestaoContagens.css';

const GestaoContagens = () => {
  const user = authService.getCurrentUser();
  const [contagens, setContagens] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [totalRegistros, setTotalRegistros] = useState(0);
  const [paginaAtual, setPaginaAtual] = useState(0);
  const registrosPorPagina = 50;
  
  // Filtros
  const [filtros, setFiltros] = useState({
    planta: user?.planta || '',
    zona_inventario: '',
    etiqueta: '',
    part_number: ''
  });
  
  // Filtros aplicados (para pesquisa)
  const [filtrosAplicados, setFiltrosAplicados] = useState({
    planta: user?.planta || '',
    zona_inventario: '',
    etiqueta: '',
    part_number: ''
  });
  
  // Modal de edição
  const [modalAberto, setModalAberto] = useState(false);
  const [contagemEditando, setContagemEditando] = useState(null);
  const [dadosEdicao, setDadosEdicao] = useState({
    etiqueta_inventario: '',
    part_number: '',
    zona_inventario: '',
    qtd: '',
    num_contagem: ''
  });
  
  // Modal de confirmação de exclusão
  const [modalExclusao, setModalExclusao] = useState(false);
  const [contagemExcluindo, setContagemExcluindo] = useState(null);

  const isAdmin = user?.role === 'ADMIN';

  useEffect(() => {
    carregarContagens();
    carregarTotal();
  }, [filtrosAplicados, paginaAtual]);

  const carregarContagens = async () => {
    setLoading(true);
    try {
      const params = {
        skip: paginaAtual * registrosPorPagina,
        limit: registrosPorPagina
      };
      
      if (filtrosAplicados.planta) params.planta = filtrosAplicados.planta;
      if (filtrosAplicados.zona_inventario) params.zona_inventario = filtrosAplicados.zona_inventario;
      if (filtrosAplicados.etiqueta) params.etiqueta = filtrosAplicados.etiqueta;
      if (filtrosAplicados.part_number) params.part_number = filtrosAplicados.part_number;
      
      const response = await api.get('/contagem/listar', { params });
      setContagens(response.data);
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Erro ao carregar contagens'
      });
    } finally {
      setLoading(false);
    }
  };

  const carregarTotal = async () => {
    try {
      const params = {};
      if (filtrosAplicados.planta) params.planta = filtrosAplicados.planta;
      if (filtrosAplicados.zona_inventario) params.zona_inventario = filtrosAplicados.zona_inventario;
      if (filtrosAplicados.etiqueta) params.etiqueta = filtrosAplicados.etiqueta;
      if (filtrosAplicados.part_number) params.part_number = filtrosAplicados.part_number;
      
      const response = await api.get('/contagem/total', { params });
      setTotalRegistros(response.data.total);
    } catch (err) {
      console.error('Erro ao carregar total:', err);
    }
  };

  const handleFiltroChange = (e) => {
    const { name, value } = e.target;
    setFiltros(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const aplicarFiltros = () => {
    setFiltrosAplicados({...filtros});
    setPaginaAtual(0);
  };

  const limparFiltros = () => {
    const filtrosLimpos = {
      planta: '',
      zona_inventario: '',
      etiqueta: '',
      part_number: ''
    };
    setFiltros(filtrosLimpos);
    setFiltrosAplicados(filtrosLimpos);
    setPaginaAtual(0);
  };

  const abrirModalEdicao = (contagem) => {
    setContagemEditando(contagem);
    setDadosEdicao({
      etiqueta_inventario: contagem.etiqueta_inventario,
      part_number: contagem.part_number,
      zona_inventario: contagem.zona_inventario,
      qtd: contagem.qtd.toString(),
      num_contagem: contagem.num_contagem.toString()
    });
    setModalAberto(true);
  };

  const fecharModalEdicao = () => {
    setModalAberto(false);
    setContagemEditando(null);
    setDadosEdicao({
      etiqueta_inventario: '',
      part_number: '',
      zona_inventario: '',
      qtd: '',
      num_contagem: ''
    });
  };

  const handleEdicaoChange = (e) => {
    const { name, value } = e.target;
    setDadosEdicao(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const salvarEdicao = async () => {
    if (!contagemEditando) return;
    
    setLoading(true);
    try {
      const dados = {
        etiqueta_inventario: dadosEdicao.etiqueta_inventario,
        part_number: dadosEdicao.part_number,
        zona_inventario: dadosEdicao.zona_inventario,
        qtd: parseFloat(dadosEdicao.qtd),
        num_contagem: parseInt(dadosEdicao.num_contagem, 10)
      };
      
      await api.put(`/contagem/${contagemEditando.id}`, dados);
      
      setMessage({
        type: 'success',
        text: 'Contagem atualizada com sucesso!'
      });
      
      fecharModalEdicao();
      carregarContagens();
      
      setTimeout(() => setMessage(null), 3000);
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Erro ao atualizar contagem'
      });
    } finally {
      setLoading(false);
    }
  };

  const abrirModalExclusao = (contagem) => {
    setContagemExcluindo(contagem);
    setModalExclusao(true);
  };

  const fecharModalExclusao = () => {
    setModalExclusao(false);
    setContagemExcluindo(null);
  };

  const confirmarExclusao = async () => {
    if (!contagemExcluindo) return;
    
    setLoading(true);
    try {
      await api.delete(`/contagem/${contagemExcluindo.id}`);
      
      setMessage({
        type: 'success',
        text: 'Contagem excluída com sucesso!'
      });
      
      fecharModalExclusao();
      carregarContagens();
      carregarTotal();
      
      setTimeout(() => setMessage(null), 3000);
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Erro ao excluir contagem'
      });
    } finally {
      setLoading(false);
    }
  };

  const formatarData = (dataString) => {
    const data = new Date(dataString);
    return data.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const totalPaginas = Math.ceil(totalRegistros / registrosPorPagina);

  return (
    <div>
      <Navbar />
      
      <div className="gestao-contagens-container">
        <div className="gestao-contagens-header">
          <h2>📋 Gestão de Contagens</h2>
          <p>Total: <strong>{totalRegistros}</strong> contagens</p>
        </div>

        {message && (
          <div className={`message ${message.type}`}>
            {message.type === 'success' ? '✅' : '⚠️'} {message.text}
          </div>
        )}

        {/* Filtros */}
        <div className="filtros-container">
          <div className="filtros-row">
            <div className="filtro-group">
              <label>Planta</label>
              <select
                name="planta"
                value={filtros.planta}
                onChange={handleFiltroChange}
              >
                <option value="">Todas</option>
                <option value="PS01">PS01</option>
                <option value="PS02">PS02</option>
                <option value="PS03">PS03</option>
                <option value="PS05">PS05</option>
                <option value="PB82">PB82</option>
              </select>
            </div>
            
            <div className="filtro-group">
              <label>Zona</label>
              <input
                type="text"
                name="zona_inventario"
                value={filtros.zona_inventario}
                onChange={handleFiltroChange}
                placeholder="Ex: A01"
              />
            </div>
            
            <div className="filtro-group">
              <label>Etiqueta</label>
              <input
                type="text"
                name="etiqueta"
                value={filtros.etiqueta}
                onChange={handleFiltroChange}
                placeholder="Ex: 12345"
              />
            </div>
            
            <div className="filtro-group">
              <label>Part Number</label>
              <input
                type="text"
                name="part_number"
                value={filtros.part_number}
                onChange={handleFiltroChange}
                placeholder="Ex: ABC123"
              />
            </div>
            
            <button onClick={aplicarFiltros} className="btn-pesquisar">
              🔍 Pesquisar
            </button>
            
            <button onClick={limparFiltros} className="btn-limpar">
              🗑️ Limpar
            </button>
          </div>
        </div>

        {/* Tabela de Contagens */}
        <div className="tabela-container">
          {loading ? (
            <div className="loading">Carregando...</div>
          ) : (
            <table className="tabela-contagens">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Planta</th>
                  <th>Zona</th>
                  <th>Etiqueta</th>
                  <th>Nº Cont.</th>
                  <th>Part Number</th>
                  <th>Qtd</th>
                  <th>Usuário</th>
                  <th>Data/Hora</th>
                  {isAdmin && <th>Ações</th>}
                </tr>
              </thead>
              <tbody>
                {contagens.length === 0 ? (
                  <tr>
                    <td colSpan={isAdmin ? 10 : 9} className="sem-dados">
                      Nenhuma contagem encontrada
                    </td>
                  </tr>
                ) : (
                  contagens.map((contagem) => (
                    <tr key={contagem.id}>
                      <td>{contagem.id}</td>
                      <td>{contagem.planta}</td>
                      <td>{contagem.zona_inventario}</td>
                      <td>{contagem.etiqueta_inventario}</td>
                      <td className="num-contagem">{contagem.num_contagem}</td>
                      <td className="part-number">{contagem.part_number}</td>
                      <td className="qtd">{contagem.qtd}</td>
                      <td>{contagem.usuario_nome}</td>
                      <td className="data">{formatarData(contagem.timestamp)}</td>
                      {isAdmin && (
                        <td className="acoes">
                          <button
                            onClick={() => abrirModalEdicao(contagem)}
                            className="btn-editar"
                            title="Editar"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => abrirModalExclusao(contagem)}
                            className="btn-excluir"
                            title="Excluir"
                          >
                            🗑️
                          </button>
                        </td>
                      )}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>

        {/* Paginação */}
        {totalPaginas > 1 && (
          <div className="paginacao">
            <button
              onClick={() => setPaginaAtual(0)}
              disabled={paginaAtual === 0}
            >
              ⏮️
            </button>
            <button
              onClick={() => setPaginaAtual(prev => Math.max(0, prev - 1))}
              disabled={paginaAtual === 0}
            >
              ◀️
            </button>
            <span>
              Página {paginaAtual + 1} de {totalPaginas}
            </span>
            <button
              onClick={() => setPaginaAtual(prev => Math.min(totalPaginas - 1, prev + 1))}
              disabled={paginaAtual >= totalPaginas - 1}
            >
              ▶️
            </button>
            <button
              onClick={() => setPaginaAtual(totalPaginas - 1)}
              disabled={paginaAtual >= totalPaginas - 1}
            >
              ⏭️
            </button>
          </div>
        )}
      </div>

      {/* Modal de Edição */}
      {modalAberto && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>✏️ Editar Contagem #{contagemEditando?.id}</h3>
              <button onClick={fecharModalEdicao} className="btn-fechar">✕</button>
            </div>
            
            <div className="modal-body">
              <div className="form-group">
                <label>Etiqueta</label>
                <input
                  type="text"
                  name="etiqueta_inventario"
                  value={dadosEdicao.etiqueta_inventario}
                  onChange={handleEdicaoChange}
                />
              </div>
              
              <div className="form-group">
                <label>Part Number</label>
                <input
                  type="text"
                  name="part_number"
                  value={dadosEdicao.part_number}
                  onChange={handleEdicaoChange}
                />
              </div>
              
              <div className="form-group">
                <label>Zona</label>
                <input
                  type="text"
                  name="zona_inventario"
                  value={dadosEdicao.zona_inventario}
                  onChange={handleEdicaoChange}
                />
              </div>
              
              <div className="form-row">
                <div className="form-group">
                  <label>Quantidade</label>
                  <input
                    type="number"
                    name="qtd"
                    value={dadosEdicao.qtd}
                    onChange={handleEdicaoChange}
                    step="0.01"
                    min="0"
                  />
                </div>
                
                <div className="form-group">
                  <label>Nº Contagem</label>
                  <input
                    type="number"
                    name="num_contagem"
                    value={dadosEdicao.num_contagem}
                    onChange={handleEdicaoChange}
                    min="1"
                    max="3"
                  />
                </div>
              </div>
            </div>
            
            <div className="modal-footer">
              <button onClick={fecharModalEdicao} className="btn-cancelar">
                Cancelar
              </button>
              <button onClick={salvarEdicao} className="btn-salvar" disabled={loading}>
                {loading ? 'Salvando...' : '💾 Salvar'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Exclusão */}
      {modalExclusao && (
        <div className="modal-overlay">
          <div className="modal-content modal-exclusao">
            <div className="modal-header">
              <h3>⚠️ Confirmar Exclusão</h3>
            </div>
            
            <div className="modal-body">
              <p>Tem certeza que deseja excluir esta contagem?</p>
              <div className="info-exclusao">
                <p><strong>ID:</strong> {contagemExcluindo?.id}</p>
                <p><strong>Etiqueta:</strong> {contagemExcluindo?.etiqueta_inventario}</p>
                <p><strong>Part Number:</strong> {contagemExcluindo?.part_number}</p>
                <p><strong>Quantidade:</strong> {contagemExcluindo?.qtd}</p>
              </div>
              <p className="aviso">Esta ação não pode ser desfeita!</p>
            </div>
            
            <div className="modal-footer">
              <button onClick={fecharModalExclusao} className="btn-cancelar">
                Cancelar
              </button>
              <button onClick={confirmarExclusao} className="btn-confirmar-excluir" disabled={loading}>
                {loading ? 'Excluindo...' : '🗑️ Excluir'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GestaoContagens;
