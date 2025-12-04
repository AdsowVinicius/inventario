import React, { useState, useEffect } from 'react';
import api from '../services/api';
import Navbar from '../components/Navbar';
import './Dashboard.css';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [plantaFiltro, setPlantaFiltro] = useState('');
  const [dashboardData, setDashboardData] = useState(null);
  const [activeTab, setActiveTab] = useState('resumo');

  const plantas = ['PS01', 'PS02', 'PS03', 'PS05', 'PB82'];

  useEffect(() => {
    carregarDashboard();
  }, [plantaFiltro]);

  const carregarDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = plantaFiltro ? { planta: plantaFiltro } : {};
      const response = await api.get('/dashboard/completo', { params });
      setDashboardData(response.data);
    } catch (err) {
      console.error('Erro ao carregar dashboard:', err);
      setError('Erro ao carregar dados do dashboard');
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('pt-BR').format(num || 0);
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'divergente': return 'status-divergente';
      case 'incompleta': return 'status-incompleta';
      case 'ok': return 'status-ok';
      default: return '';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'divergente': return '⚠️ Divergente';
      case 'incompleta': return '⏳ Incompleta';
      case 'ok': return '✅ OK';
      default: return status;
    }
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="dashboard-container">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Carregando dashboard...</p>
          </div>
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Navbar />
        <div className="dashboard-container">
          <div className="error-container">
            <p>{error}</p>
            <button onClick={carregarDashboard} className="btn-retry">
              Tentar novamente
            </button>
          </div>
        </div>
      </>
    );
  }

  if (!dashboardData) return <><Navbar /><div className="dashboard-container"></div></>;

  const { kpis, divergentes, progresso_zonas, contagens_por_usuario, contagens_por_planta, resumo_divergencias } = dashboardData;

  return (
    <>
      <Navbar />
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1>📊 Dashboard de Inventário</h1>
        <div className="filtro-planta">
          <label>Planta:</label>
          <select 
            value={plantaFiltro} 
            onChange={(e) => setPlantaFiltro(e.target.value)}
          >
            <option value="">Todas</option>
            {plantas.map(p => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
          <button onClick={carregarDashboard} className="btn-atualizar">
            🔄 Atualizar
          </button>
        </div>
      </div>

      {/* KPIs Cards */}
      <div className="kpis-grid">
        <div className="kpi-card">
          <div className="kpi-icon">📝</div>
          <div className="kpi-content">
            <span className="kpi-value">{formatNumber(kpis.total_contagens)}</span>
            <span className="kpi-label">Total de Contagens</span>
          </div>
        </div>
        
        <div className="kpi-card">
          <div className="kpi-icon">🏷️</div>
          <div className="kpi-content">
            <span className="kpi-value">{formatNumber(kpis.total_etiquetas)}</span>
            <span className="kpi-label">Etiquetas Únicas</span>
          </div>
        </div>
        
        <div className="kpi-card">
          <div className="kpi-icon">📦</div>
          <div className="kpi-content">
            <span className="kpi-value">{formatNumber(kpis.total_itens_base)}</span>
            <span className="kpi-label">Itens na Base</span>
          </div>
        </div>
        
        <div className="kpi-card highlight-today">
          <div className="kpi-icon">📅</div>
          <div className="kpi-content">
            <span className="kpi-value">{formatNumber(kpis.contagens_hoje)}</span>
            <span className="kpi-label">Contagens Hoje</span>
          </div>
        </div>
        
        <div className="kpi-card">
          <div className="kpi-icon">📆</div>
          <div className="kpi-content">
            <span className="kpi-value">{formatNumber(kpis.contagens_semana)}</span>
            <span className="kpi-label">Contagens na Semana</span>
          </div>
        </div>
        
        <div className="kpi-card">
          <div className="kpi-icon">👥</div>
          <div className="kpi-content">
            <span className="kpi-value">{formatNumber(kpis.usuarios_ativos)}</span>
            <span className="kpi-label">Usuários Ativos</span>
          </div>
        </div>
        
        <div className="kpi-card">
          <div className="kpi-icon">🗺️</div>
          <div className="kpi-content">
            <span className="kpi-value">{formatNumber(kpis.zonas_ativas)}</span>
            <span className="kpi-label">Zonas Ativas</span>
          </div>
        </div>
        
        <div className={`kpi-card ${resumo_divergencias.total_divergentes > 0 ? 'highlight-warning' : 'highlight-success'}`}>
          <div className="kpi-icon">⚠️</div>
          <div className="kpi-content">
            <span className="kpi-value">{formatNumber(resumo_divergencias.total_divergentes)}</span>
            <span className="kpi-label">Divergências</span>
          </div>
        </div>
      </div>

      {/* Tabs de navegação */}
      <div className="dashboard-tabs">
        <button 
          className={`tab-btn ${activeTab === 'resumo' ? 'active' : ''}`}
          onClick={() => setActiveTab('resumo')}
        >
          📈 Resumo
        </button>
        <button 
          className={`tab-btn ${activeTab === 'divergentes' ? 'active' : ''}`}
          onClick={() => setActiveTab('divergentes')}
        >
          ⚠️ Divergências ({divergentes.filter(d => d.status === 'divergente').length})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'incompletas' ? 'active' : ''}`}
          onClick={() => setActiveTab('incompletas')}
        >
          ⏳ Incompletas ({divergentes.filter(d => d.status === 'incompleta').length})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'zonas' ? 'active' : ''}`}
          onClick={() => setActiveTab('zonas')}
        >
          🗺️ Zonas
        </button>
        <button 
          className={`tab-btn ${activeTab === 'usuarios' ? 'active' : ''}`}
          onClick={() => setActiveTab('usuarios')}
        >
          👥 Usuários
        </button>
      </div>

      {/* Conteúdo das tabs */}
      <div className="tab-content">
        {activeTab === 'resumo' && (
          <div className="resumo-section">
            <div className="resumo-cards">
              <div className="resumo-card">
                <h3>📊 Resumo por Planta</h3>
                <table className="dashboard-table">
                  <thead>
                    <tr>
                      <th>Planta</th>
                      <th>Contagens</th>
                      <th>Etiquetas</th>
                      <th>Completas</th>
                      <th>Divergências</th>
                    </tr>
                  </thead>
                  <tbody>
                    {contagens_por_planta.map((p, idx) => (
                      <tr key={idx}>
                        <td><strong>{p.planta}</strong></td>
                        <td>{formatNumber(p.total_contagens)}</td>
                        <td>{formatNumber(p.etiquetas_unicas)}</td>
                        <td>{formatNumber(p.contagens_completas)}</td>
                        <td className={p.divergencias > 0 ? 'td-warning' : 'td-success'}>
                          {formatNumber(p.divergencias)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="resumo-card">
                <h3>📈 Indicadores de Qualidade</h3>
                <div className="indicadores-grid">
                  <div className="indicador">
                    <span className="indicador-label">Taxa de Conclusão</span>
                    <span className="indicador-value">
                      {kpis.total_etiquetas > 0 
                        ? Math.round((contagens_por_planta.reduce((acc, p) => acc + p.contagens_completas, 0) / kpis.total_etiquetas) * 100)
                        : 0}%
                    </span>
                  </div>
                  <div className="indicador">
                    <span className="indicador-label">Taxa de Divergência</span>
                    <span className={`indicador-value ${resumo_divergencias.percentual_problemas > 10 ? 'valor-warning' : 'valor-success'}`}>
                      {resumo_divergencias.percentual_problemas}%
                    </span>
                  </div>
                  <div className="indicador">
                    <span className="indicador-label">Contagens Incompletas</span>
                    <span className="indicador-value">{resumo_divergencias.total_incompletas}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'divergentes' && (
          <div className="divergentes-section">
            <h3>⚠️ Contagens Divergentes</h3>
            <p className="section-description">
              Etiquetas onde as 2 contagens apresentam valores diferentes.
            </p>
            {divergentes.filter(d => d.status === 'divergente').length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon">✅</span>
                <p>Nenhuma divergência encontrada!</p>
              </div>
            ) : (
              <div className="table-container">
                <table className="dashboard-table divergentes-table">
                  <thead>
                    <tr>
                      <th>Etiqueta</th>
                      <th>Part Number</th>
                      <th>Planta</th>
                      <th>Zona</th>
                      <th>1ª Contagem</th>
                      <th>2ª Contagem</th>
                      <th>3ª Contagem</th>
                      <th>Diferença</th>
                    </tr>
                  </thead>
                  <tbody>
                    {divergentes
                      .filter(d => d.status === 'divergente')
                      .map((d, idx) => (
                        <tr key={idx} className="row-divergente">
                          <td><strong>{d.etiqueta_inventario}</strong></td>
                          <td>{d.part_number}</td>
                          <td>{d.planta}</td>
                          <td>{d.zona_inventario}</td>
                          <td>
                            {d.contagem_1 !== null ? formatNumber(d.contagem_1) : '-'}
                            {d.usuario_1 && <small className="usuario-info">({d.usuario_1})</small>}
                          </td>
                          <td>
                            {d.contagem_2 !== null ? formatNumber(d.contagem_2) : '-'}
                            {d.usuario_2 && <small className="usuario-info">({d.usuario_2})</small>}
                          </td>
                          <td>
                            {d.contagem_3 !== null ? formatNumber(d.contagem_3) : '-'}
                            {d.usuario_3 && <small className="usuario-info">({d.usuario_3})</small>}
                          </td>
                          <td className="td-warning">
                            <strong>{formatNumber(d.diferenca_maxima)}</strong>
                          </td>
                        </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'incompletas' && (
          <div className="incompletas-section">
            <h3>⏳ Contagens Incompletas</h3>
            <p className="section-description">
              Etiquetas que ainda não tiveram as 3 contagens realizadas.
            </p>
            {divergentes.filter(d => d.status === 'incompleta').length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon">✅</span>
                <p>Todas as contagens estão completas!</p>
              </div>
            ) : (
              <div className="table-container">
                <table className="dashboard-table">
                  <thead>
                    <tr>
                      <th>Etiqueta</th>
                      <th>Part Number</th>
                      <th>Planta</th>
                      <th>Zona</th>
                      <th>1ª Contagem</th>
                      <th>2ª Contagem</th>
                      <th>3ª Contagem</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {divergentes
                      .filter(d => d.status === 'incompleta')
                      .map((d, idx) => (
                        <tr key={idx} className="row-incompleta">
                          <td><strong>{d.etiqueta_inventario}</strong></td>
                          <td>{d.part_number}</td>
                          <td>{d.planta}</td>
                          <td>{d.zona_inventario}</td>
                          <td>{d.contagem_1 !== null ? formatNumber(d.contagem_1) : <span className="pendente">Pendente</span>}</td>
                          <td>{d.contagem_2 !== null ? formatNumber(d.contagem_2) : <span className="pendente">Pendente</span>}</td>
                          <td>{d.contagem_3 !== null ? formatNumber(d.contagem_3) : <span className="pendente">Pendente</span>}</td>
                          <td>
                            <span className="status-badge incompleta">
                              {[d.contagem_1, d.contagem_2, d.contagem_3].filter(c => c !== null).length}/3
                            </span>
                          </td>
                        </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'zonas' && (
          <div className="zonas-section">
            <h3>🗺️ Progresso por Zona</h3>
            {progresso_zonas.length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon">📭</span>
                <p>Nenhuma zona com contagens</p>
              </div>
            ) : (
              <div className="zonas-grid">
                {progresso_zonas.map((zona, idx) => (
                  <div key={idx} className="zona-card">
                    <div className="zona-header">
                      <h4>{zona.zona}</h4>
                      <span className="zona-planta">{zona.planta}</span>
                    </div>
                    <div className="zona-progress">
                      <div 
                        className="progress-bar"
                        style={{ width: `${zona.percentual_completo}%` }}
                      ></div>
                    </div>
                    <div className="zona-stats">
                      <div className="zona-stat">
                        <span className="stat-value">{zona.etiquetas_contadas}</span>
                        <span className="stat-label">Etiquetas</span>
                      </div>
                      <div className="zona-stat">
                        <span className="stat-value success">{zona.contagens_completas}</span>
                        <span className="stat-label">Completas</span>
                      </div>
                      <div className="zona-stat">
                        <span className="stat-value warning">{zona.contagens_parciais}</span>
                        <span className="stat-label">Parciais</span>
                      </div>
                      <div className="zona-stat">
                        <span className="stat-value">{zona.percentual_completo}%</span>
                        <span className="stat-label">Progresso</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'usuarios' && (
          <div className="usuarios-section">
            <h3>👥 Contagens por Usuário</h3>
            {contagens_por_usuario.length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon">👤</span>
                <p>Nenhum usuário realizou contagens</p>
              </div>
            ) : (
              <div className="table-container">
                <table className="dashboard-table">
                  <thead>
                    <tr>
                      <th>Usuário</th>
                      <th>Total de Contagens</th>
                      <th>Contagens Hoje</th>
                      <th>Média Diária</th>
                    </tr>
                  </thead>
                  <tbody>
                    {contagens_por_usuario.map((u, idx) => (
                      <tr key={idx}>
                        <td><strong>{u.usuario_nome}</strong></td>
                        <td>{formatNumber(u.total_contagens)}</td>
                        <td className={u.contagens_hoje > 0 ? 'td-success' : ''}>
                          {formatNumber(u.contagens_hoje)}
                        </td>
                        <td>{Math.round(u.total_contagens / 7)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
    </>
  );
};

export default Dashboard;
