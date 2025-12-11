import React, { useState } from 'react';
import { authService, exportacaoService } from '../services/api';
import Navbar from '../components/Navbar';
import './Exportacao.css';

const PLANTAS = ['PS01', 'PS02', 'PS03', 'PS05', 'PB82'];

const Exportacao = () => {
  const [filtros, setFiltros] = useState({
    planta: '',
    zona_inventario: '',
    etiqueta_inventario: '',
    part_number: '',
    num_contagem: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFiltros(prev => ({
      ...prev,
      [name]: value
    }));
    setMessage(null);
  };
  
  const limparFiltros = () => {
    setFiltros({
      planta: '',
      zona_inventario: '',
      etiqueta_inventario: '',
      part_number: '',
      num_contagem: ''
    });
    setMessage(null);
    setPreviewData(null);
  };
  
  const prepararFiltros = () => {
    // Remover campos vazios
    const filtrosLimpos = {};
    
    Object.keys(filtros).forEach(key => {
      if (filtros[key]) {
        filtrosLimpos[key] = filtros[key];
      }
    });
    
    return filtrosLimpos;
  };
  
  const handlePreview = async () => {
    setLoadingPreview(true);
    setMessage(null);
    
    try {
      const response = await exportacaoService.preview(prepararFiltros());
      setPreviewData(response);
      
      if (response.total === 0) {
        setMessage({
          type: 'error',
          text: '⚠️ Nenhum registro encontrado com os filtros aplicados'
        });
      }
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Erro ao carregar preview'
      });
      setPreviewData(null);
    } finally {
      setLoadingPreview(false);
    }
  };
  
  const handleExportarCSV = async () => {
    setLoading(true);
    setMessage(null);
    
    try {
      await exportacaoService.exportarCSV(prepararFiltros());
      
      setMessage({
        type: 'success',
        text: '✅ Arquivo CSV exportado com sucesso!'
      });
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Erro ao exportar CSV'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleExportarExcel = async () => {
    setLoading(true);
    setMessage(null);
    
    try {
      await exportacaoService.exportarExcel(prepararFiltros());
      
      setMessage({
        type: 'success',
        text: '✅ Arquivo Excel exportado com sucesso!'
      });
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Erro ao exportar Excel'
      });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <Navbar />
      
      <div className="exportacao-container">
        <div className="exportacao-card">
          <h2>Exportação de Contagens</h2>
          <p className="subtitle">Filtre os dados e exporte para CSV ou Excel</p>
          
          {message && (
            <div className={`message ${message.type}`}>
              {message.text}
            </div>
          )}
          
          <div className="filtros-form">
            <h3>Filtros (Todos Opcionais)</h3>
            
            <div className="form-row">
              <div className="form-group">
                <label>Planta</label>
                <select
                  name="planta"
                  value={filtros.planta}
                  onChange={handleChange}
                >
                  <option value="">Todas</option>
                  {PLANTAS.map(p => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>
              
              <div className="form-group">
                <label>Zona de Inventário</label>
                <input
                  type="text"
                  name="zona_inventario"
                  value={filtros.zona_inventario}
                  onChange={handleChange}
                  placeholder="Ex: ZONA-A"
                />
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label>Etiqueta de Inventário</label>
                <input
                  type="text"
                  name="etiqueta_inventario"
                  value={filtros.etiqueta_inventario}
                  onChange={handleChange}
                  placeholder="Ex: ETQ-001"
                />
              </div>
              
              <div className="form-group">
                <label>Part Number</label>
                <input
                  type="text"
                  name="part_number"
                  value={filtros.part_number}
                  onChange={handleChange}
                  placeholder="Ex: PN-12345"
                />
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label>Número da Contagem (1-3)</label>
                <input
                  type="number"
                  name="num_contagem"
                  value={filtros.num_contagem}
                  onChange={handleChange}
                  placeholder="1, 2 ou 3"
                  min="1"
                  max="3"
                />
              </div>
              
              <div className="form-group">
                <button 
                  onClick={limparFiltros}
                  className="btn-limpar"
                  type="button"
                >
                  Limpar Filtros
                </button>
              </div>
              
              <div className="form-group">
                <button 
                  onClick={handlePreview}
                  className="btn-preview"
                  type="button"
                  disabled={loadingPreview}
                >
                  {loadingPreview ? 'Carregando...' : 'Visualizar Dados'}
                </button>
              </div>
            </div>
          </div>
          
          {previewData && (
            <div className="preview-section">
              <div className="preview-header">
                <h3>Visualização dos Dados</h3>
                <span className="preview-count">
                  Exibindo {previewData.exibindo} de {previewData.total} registros
                </span>
              </div>
              
              <div className="table-container">
                <table className="preview-table">
                  <thead>
                    <tr>
                      <th>Num. Contagem</th>
                      <th>Num. Etiqueta</th>
                      <th>Material</th>
                      <th>Planta</th>
                      <th>Qtd</th>
                      <th>Zona</th>
                      <th>Data Criação</th>
                      <th>Modificação</th>
                      <th>Criado Por</th>
                      <th>Lote</th>
                    </tr>
                  </thead>
                  <tbody>
                    {previewData.dados.map((item, idx) => (
                      <tr key={item.id || idx}>
                        <td><span className="badge badge-contagem">{item.etiqueta_inventario}</span></td>
                        <td><span className="badge badge-etiqueta">{item.inventario_cod_texto}</span></td>
                        <td className="material-cell">{item.part_number_text}</td>
                        <td><span className="badge badge-planta">{item.planta_text}</span></td>
                        <td className="quantidade-cell">{item.quantidade}</td>
                        <td>{item.zona_invent_no_text || '-'}</td>
                        <td className="data-cell">{item.created_date}</td>
                        <td className="data-cell">{item.modified_date || '-'}</td>
                        <td>{item.created_by}</td>
                        <td>{item.lote || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {previewData.total > previewData.exibindo && (
                <p className="preview-note">
                  Exibindo apenas {previewData.exibindo} registros. 
                  Use a exportação para obter todos os {previewData.total} registros.
                </p>
              )}
            </div>
          )}
          
          <div className="exportacao-actions">
            <h3>Exportar Dados</h3>
            
            <div className="buttons-row">
              <button
                onClick={handleExportarCSV}
                className="btn-export btn-csv"
                disabled={loading}
              >
                {loading ? 'Exportando...' : 'Exportar CSV'}
              </button>
              
              <button
                onClick={handleExportarExcel}
                className="btn-export btn-excel"
                disabled={loading}
              >
                {loading ? 'Exportando...' : 'Exportar Excel'}
              </button>
            </div>
            
            <div className="info-box">
              <p>
                <strong>Dica:</strong> Se nenhum filtro for aplicado, 
                todos os registros serão exportados.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Exportacao;
