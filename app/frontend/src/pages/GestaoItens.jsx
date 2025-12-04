import React, { useState, useEffect } from 'react';
import { authService, itensService } from '../services/api';
import Navbar from '../components/Navbar';
import './GestaoItens.css';

const PLANTAS = ['PS01', 'PS02', 'PS03', 'PS05', 'PS09', 'PB82'];
const UNIDADES = ['UN', 'KG', 'M', 'M2', 'M3', 'L', 'PC', 'CX', 'PAR', 'JG', 'KIT', 'ROL', 'FD', 'GL'];

const GestaoItens = () => {
  const user = authService.getCurrentUser();
  const isAdmin = user?.role === 'ADMIN';
  const [itens, setItens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);
  
  // Filtros
  const [filtroPlanta, setFiltroPlanta] = useState('');
  const [filtroBusca, setFiltroBusca] = useState('');
  
  // Paginação
  const [pagina, setPagina] = useState(0);
  const [totalItens, setTotalItens] = useState(0);
  const itensPorPagina = 20;
  
  // Modal de edição/criação
  const [modalAberto, setModalAberto] = useState(false);
  const [itemEditando, setItemEditando] = useState(null);
  const [formData, setFormData] = useState({
    num_material: '',
    txt_descrica_material: '',
    planta: user?.planta || 'PS01',
    deposito: '',
    tipo_material: '',
    und_medida: ''
  });
  const [salvando, setSalvando] = useState(false);
  
  // Modal de confirmação de exclusão
  const [modalExclusao, setModalExclusao] = useState(false);
  const [itemExcluir, setItemExcluir] = useState(null);
  const [excluindo, setExcluindo] = useState(false);

  // Carregar itens
  useEffect(() => {
    carregarItens();
  }, [filtroPlanta, pagina]);

  // Resetar página ao mudar filtros
  useEffect(() => {
    setPagina(0);
  }, [filtroPlanta, filtroBusca]);

  const carregarItens = async () => {
    setLoading(true);
    try {
      const [dados, contagem] = await Promise.all([
        itensService.listar(filtroPlanta, filtroBusca, pagina * itensPorPagina, itensPorPagina),
        itensService.contarTotal(filtroPlanta, filtroBusca)
      ]);
      setItens(dados);
      setTotalItens(contagem.total);
    } catch (err) {
      console.error('Erro ao carregar itens:', err);
      setMessage({
        type: 'error',
        text: 'Erro ao carregar itens'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleBuscar = (e) => {
    e.preventDefault();
    carregarItens();
  };

  const abrirModalNovo = () => {
    setItemEditando(null);
    setFormData({
      num_material: '',
      txt_descrica_material: '',
      planta: user?.planta || 'PS01',
      deposito: '',
      tipo_material: '',
      und_medida: ''
    });
    setModalAberto(true);
  };

  const abrirModalEditar = (item) => {
    setItemEditando(item);
    setFormData({
      num_material: item.num_material || '',
      txt_descrica_material: item.txt_descrica_material || '',
      planta: item.planta || 'PS01',
      deposito: item.deposito || '',
      tipo_material: item.tipo_material || '',
      und_medida: item.und_medida || ''
    });
    setModalAberto(true);
  };

  const fecharModal = () => {
    setModalAberto(false);
    setItemEditando(null);
    setFormData({
      num_material: '',
      txt_descrica_material: '',
      planta: user?.planta || 'PS01',
      deposito: '',
      tipo_material: '',
      und_medida: ''
    });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSalvando(true);
    setMessage(null);

    try {
      if (itemEditando) {
        await itensService.atualizar(itemEditando.id, formData);
        setMessage({
          type: 'success',
          text: 'Item atualizado com sucesso!'
        });
      } else {
        await itensService.criar(formData);
        setMessage({
          type: 'success',
          text: 'Item criado com sucesso!'
        });
      }
      
      fecharModal();
      carregarItens();
      
      setTimeout(() => setMessage(null), 3000);
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Erro ao salvar item'
      });
    } finally {
      setSalvando(false);
    }
  };

  const abrirModalExclusao = (item) => {
    setItemExcluir(item);
    setModalExclusao(true);
  };

  const fecharModalExclusao = () => {
    setModalExclusao(false);
    setItemExcluir(null);
  };

  const confirmarExclusao = async () => {
    if (!itemExcluir) return;
    
    setExcluindo(true);
    try {
      await itensService.excluir(itemExcluir.id);
      setMessage({
        type: 'success',
        text: 'Item excluído com sucesso!'
      });
      fecharModalExclusao();
      carregarItens();
      
      setTimeout(() => setMessage(null), 3000);
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Erro ao excluir item'
      });
    } finally {
      setExcluindo(false);
    }
  };

  const totalPaginas = Math.ceil(totalItens / itensPorPagina);

  return (
    <div>
      <Navbar />
      
      <div className="gestao-itens-container">
        <div className="gestao-itens-card">
          <div className="gestao-header">
            <h2>📦 Gestão de Itens do Inventário</h2>
            <button onClick={abrirModalNovo} className="btn-novo">
              ➕ Novo Item
            </button>
          </div>
          
          {message && (
            <div className={`message ${message.type}`}>
              {message.type === 'success' ? '✅' : '⚠️'} {message.text}
            </div>
          )}
          
          {/* Filtros */}
          <form onSubmit={handleBuscar} className="filtros-form">
            <div className="filtros-row">
              <div className="filtro-group">
                <label>Planta</label>
                <select 
                  value={filtroPlanta} 
                  onChange={(e) => setFiltroPlanta(e.target.value)}
                >
                  <option value="">Todas</option>
                  {PLANTAS.map(p => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>
              
              <div className="filtro-group filtro-busca">
                <label>Buscar</label>
                <input
                  type="text"
                  value={filtroBusca}
                  onChange={(e) => setFiltroBusca(e.target.value)}
                  placeholder="Part Number ou Descrição..."
                />
              </div>
              
              <button type="submit" className="btn-filtrar">
                🔍 Filtrar
              </button>
            </div>
          </form>
          
          {/* Tabela de itens */}
          <div className="tabela-container">
            {loading ? (
              <div className="loading">Carregando...</div>
            ) : itens.length === 0 ? (
              <div className="sem-dados">Nenhum item encontrado</div>
            ) : (
              <table className="tabela-itens">
                <thead>
                  <tr>
                    <th>Part Number</th>
                    <th>Descrição</th>
                    <th>Planta</th>
                    <th>Depósito</th>
                    <th>Tipo</th>
                    <th>Unidade</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {itens.map(item => (
                    <tr key={item.id}>
                      <td className="pn-cell">{item.num_material}</td>
                      <td className="desc-cell" title={item.txt_descrica_material}>
                        {item.txt_descrica_material || '-'}
                      </td>
                      <td>{item.planta}</td>
                      <td>{item.deposito || '-'}</td>
                      <td>{item.tipo_material || '-'}</td>
                      <td>{item.und_medida || '-'}</td>
                      <td className="acoes-cell">
                        <button 
                          onClick={() => abrirModalEditar(item)}
                          className="btn-acao btn-editar"
                          title="Editar"
                        >
                          ✏️
                        </button>
                        {isAdmin && (
                          <button 
                            onClick={() => abrirModalExclusao(item)}
                            className="btn-acao btn-excluir"
                            title="Excluir"
                          >
                            🗑️
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
          
          {/* Paginação */}
          {totalPaginas > 1 && (
            <div className="paginacao">
              <button 
                onClick={() => setPagina(p => Math.max(0, p - 1))}
                disabled={pagina === 0}
                className="btn-paginacao"
              >
                ◀ Anterior
              </button>
              
              <span className="info-paginacao">
                Página {pagina + 1} de {totalPaginas} ({totalItens} itens)
              </span>
              
              <button 
                onClick={() => setPagina(p => Math.min(totalPaginas - 1, p + 1))}
                disabled={pagina >= totalPaginas - 1}
                className="btn-paginacao"
              >
                Próxima ▶
              </button>
            </div>
          )}
        </div>
      </div>
      
      {/* Modal de Criação/Edição */}
      {modalAberto && (
        <div className="modal-overlay" onClick={fecharModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{itemEditando ? '✏️ Editar Item' : '➕ Novo Item'}</h3>
              <button onClick={fecharModal} className="btn-fechar">✕</button>
            </div>
            
            <form onSubmit={handleSubmit} className="modal-form">
              <div className="form-row">
                <div className="form-group">
                  <label>Part Number *</label>
                  <input
                    type="text"
                    name="num_material"
                    value={formData.num_material}
                    onChange={handleChange}
                    required
                    placeholder="Ex: 12345678"
                  />
                </div>
                
                <div className="form-group">
                  <label>Planta *</label>
                  <select
                    name="planta"
                    value={formData.planta}
                    onChange={handleChange}
                    required
                  >
                    {PLANTAS.map(p => (
                      <option key={p} value={p}>{p}</option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div className="form-group">
                <label>Descrição</label>
                <input
                  type="text"
                  name="txt_descrica_material"
                  value={formData.txt_descrica_material}
                  onChange={handleChange}
                  placeholder="Descrição do material..."
                />
              </div>
              
              <div className="form-row">
                <div className="form-group">
                  <label>Depósito</label>
                  <input
                    type="text"
                    name="deposito"
                    value={formData.deposito}
                    onChange={handleChange}
                    placeholder="Ex: DEP01"
                  />
                </div>
                
                <div className="form-group">
                  <label>Tipo Material</label>
                  <input
                    type="text"
                    name="tipo_material"
                    value={formData.tipo_material}
                    onChange={handleChange}
                    placeholder="Ex: PEÇAS"
                  />
                </div>
                
                <div className="form-group">
                  <label>Unidade Medida</label>
                  <select
                    name="und_medida"
                    value={formData.und_medida}
                    onChange={handleChange}
                  >
                    <option value="">Selecione</option>
                    {UNIDADES.map(u => (
                      <option key={u} value={u}>{u}</option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div className="modal-actions">
                <button 
                  type="button" 
                  onClick={fecharModal}
                  className="btn-cancelar"
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  className="btn-salvar"
                  disabled={salvando}
                >
                  {salvando ? 'Salvando...' : (itemEditando ? 'Atualizar' : 'Criar')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {/* Modal de Confirmação de Exclusão */}
      {modalExclusao && itemExcluir && (
        <div className="modal-overlay" onClick={fecharModalExclusao}>
          <div className="modal-content modal-exclusao" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header modal-header-danger">
              <h3>⚠️ Confirmar Exclusão</h3>
              <button onClick={fecharModalExclusao} className="btn-fechar">✕</button>
            </div>
            
            <div className="modal-body">
              <p>Tem certeza que deseja excluir o item:</p>
              <div className="item-exclusao-info">
                <strong>Part Number:</strong> {itemExcluir.num_material}<br />
                <strong>Descrição:</strong> {itemExcluir.txt_descrica_material || 'N/A'}<br />
                <strong>Planta:</strong> {itemExcluir.planta}
              </div>
              <p className="aviso-exclusao">Esta ação não pode ser desfeita!</p>
            </div>
            
            <div className="modal-actions">
              <button 
                type="button" 
                onClick={fecharModalExclusao}
                className="btn-cancelar"
              >
                Cancelar
              </button>
              <button 
                type="button" 
                onClick={confirmarExclusao}
                className="btn-excluir-confirmar"
                disabled={excluindo}
              >
                {excluindo ? 'Excluindo...' : '🗑️ Excluir'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GestaoItens;
