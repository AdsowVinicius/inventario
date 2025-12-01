import React, { useState, useEffect } from 'react';
import { authService, itensService, contagemService } from '../services/api';
import Navbar from '../components/Navbar';
import './Contagem.css';

const PLANTAS = ['PS01', 'PS02', 'PS03', 'PS05', 'PS09', 'PB82'];

// Zonas específicas por planta
const ZONAS_POR_PLANTA = {
  'PS01': ['ZONA-A', 'ZONA-B', 'ZONA-C', 'ZONA-D'],
  'PS02': ['ZONA-A', 'ZONA-B', 'ZONA-C'],
  'PS03': ['ZONA-A', 'ZONA-B'],
  'PS05': ['ZONA-A', 'ZONA-B', 'ZONA-C', 'ZONA-D', 'ZONA-E'],
  'PS09': ['ZONA-A', 'ZONA-B', 'ZONA-C'],
  'PB82': ['ZONA-A', 'ZONA-B']
};

const Contagem = () => {
  const user = authService.getCurrentUser();
  
  // Estado para controlar a etapa
  const [etapa, setEtapa] = useState(1); // 1 = Selecionar Zona, 2 = Fazer Contagens
  const [zonaAtual, setZonaAtual] = useState({
    planta: user?.planta || 'PS01',
    zona_inventario: ''
  });
  
  const [formData, setFormData] = useState({
    num_contagem: 1,
    etiqueta_inventario: '',
    part_number: '',
    campo: '',
    qtd: 0
  });
  
  const [partNumbers, setPartNumbers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [autoSugestao, setAutoSugestao] = useState(true);
  const [contagensRealizadas, setContagensRealizadas] = useState(0);
  const [zonasDisponiveis, setZonasDisponiveis] = useState(
    ZONAS_POR_PLANTA[user?.planta || 'PS01'] || []
  );
  
  // Planta fixa do usuário
  const plantaUsuario = user?.planta || 'PS01';
  
  // Carregar part numbers
  useEffect(() => {
    if (etapa === 2) {
      carregarPartNumbers(plantaUsuario);
    }
  }, [etapa, plantaUsuario]);
  
  const carregarPartNumbers = async (planta) => {
    try {
      const data = await itensService.listarPartNumbers(planta);
      setPartNumbers(data);
    } catch (err) {
      console.error('Erro ao carregar part numbers:', err);
    }
  };
  
  // Função para iniciar contagens na zona
  const iniciarContagens = (e) => {
    e.preventDefault();
    setEtapa(2);
    setMessage(null);
    setContagensRealizadas(0);
  };
  
  // Função para mudar de zona
  const mudarZona = () => {
    const confirmar = window.confirm(
      `Você realizou ${contagensRealizadas} contagem(ns) nesta zona.\n\nDeseja realmente mudar de zona?`
    );
    
    if (!confirmar) {
      return;
    }
    
    setEtapa(1);
    setZonaAtual({
      planta: plantaUsuario,
      zona_inventario: ''
    });
    setFormData({
      num_contagem: 1,
      etiqueta_inventario: '',
      part_number: '',
      campo: '',
      qtd: 0
    });
    setMessage(null);
    setContagensRealizadas(0);
  };
  
  const handleZonaChange = (e) => {
    const { name, value } = e.target;
    setZonaAtual(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  // Sugerir número de contagem automaticamente
  const sugerirNumeroContagem = async () => {
    if (!formData.part_number || !formData.etiqueta_inventario || !autoSugestao) {
      return;
    }
    
    try {
      const response = await contagemService.sugerirNumero(
        formData.part_number,
        formData.etiqueta_inventario,
        plantaUsuario
      );
      
      setFormData(prev => ({
        ...prev,
        num_contagem: response.num_contagem_sugerido
      }));
    } catch (err) {
      console.error('Erro ao sugerir número:', err);
    }
  };
  
  // Disparar sugestão quando mudar part number ou etiqueta
  useEffect(() => {
    if (formData.part_number && formData.etiqueta_inventario) {
      sugerirNumeroContagem();
    }
  }, [formData.part_number, formData.etiqueta_inventario, plantaUsuario]);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'qtd' || name === 'num_contagem' ? parseFloat(value) || 0 : value
    }));
    setMessage(null);
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    
    try {
      // Combinar dados da zona com dados da contagem
      const dadosCompletos = {
        ...zonaAtual,
        ...formData
      };
      
      const response = await contagemService.salvar(dadosCompletos);
      
      setMessage({
        type: 'success',
        text: response.mensagem
      });
      
      // Incrementar contador
      setContagensRealizadas(prev => prev + 1);
      
      // Limpar apenas os campos da contagem, manter zona
      setFormData({
        num_contagem: 1,
        etiqueta_inventario: '',
        part_number: '',
        campo: '',
        qtd: 0
      });
      
      // Limpar mensagem após 3 segundos
      setTimeout(() => setMessage(null), 3000);
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Erro ao salvar contagem'
      });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <Navbar />
      
      <div className="contagem-container">
        <div className="contagem-card">
          {etapa === 1 ? (
            // ETAPA 1: Selecionar Zona
            <>
              <h2>📍 Etapa 1: Selecionar Zona de Inventário</h2>
              <p className="subtitle">Sua planta: <strong>{plantaUsuario}</strong> - Selecione a zona onde realizará as contagens</p>
              
              <form onSubmit={iniciarContagens} className="contagem-form">
                <div className="form-group">
                  <label>Zona de Inventário *</label>
                  <select
                    name="zona_inventario"
                    value={zonaAtual.zona_inventario}
                    onChange={handleZonaChange}
                    required
                    autoFocus
                  >
                    <option value="">Selecione uma zona</option>
                    {zonasDisponiveis.map(zona => (
                      <option key={zona} value={zona}>{zona}</option>
                    ))}
                  </select>
                </div>
                
                <button 
                  type="submit" 
                  className="btn-submit"
                >
                  ➡️ Iniciar Contagens nesta Zona
                </button>
              </form>
            </>
          ) : (
            // ETAPA 2: Fazer Contagens
            <>
              <div className="zona-header">
                <div className="zona-info">
                  <h2>📝 Contagens na Zona</h2>
                  <div className="zona-badge">
                    <strong>Planta:</strong> {zonaAtual.planta} | <strong>Zona:</strong> {zonaAtual.zona_inventario}
                  </div>
                  <div className="contagens-counter">
                    ✅ Contagens realizadas: <strong>{contagensRealizadas}</strong>
                  </div>
                </div>
                <button 
                  onClick={mudarZona}
                  className="btn-mudar-zona"
                  type="button"
                >
                  🔄 Mudar de Zona
                </button>
              </div>
              
              {message && (
                <div className={`message ${message.type}`}>
                  {message.type === 'success' ? '✅' : '⚠️'} {message.text}
                </div>
              )}
              
              <form onSubmit={handleSubmit} className="contagem-form">
                <div className="form-row">
                  <div className="form-group">
                    <label>
                      Número da Contagem *
                      <label className="checkbox-inline">
                        <input
                          type="checkbox"
                          checked={autoSugestao}
                          onChange={(e) => setAutoSugestao(e.target.checked)}
                        />
                        Auto
                      </label>
                    </label>
                    <input
                      type="number"
                      name="num_contagem"
                      value={formData.num_contagem}
                      onChange={handleChange}
                      min="1"
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Etiqueta de Inventário *</label>
                    <input
                      type="number"
                      name="etiqueta_inventario"
                      value={formData.etiqueta_inventario}
                      onChange={handleChange}
                      placeholder="Ex: 12345"
                      required
                      min="0"
                      step="1"
                      autoFocus
                    />
                  </div>
                </div>
                
                <div className="form-group">
                  <label>Part Number (Código de Barras) *</label>
                  <input
                    type="number"
                    name="part_number"
                    value={formData.part_number}
                    onChange={handleChange}
                    placeholder="Digite ou escaneie o código numérico"
                    required
                    min="0"
                    step="1"
                  />
                </div>
                
                <div className="form-group">
                  <label>Campo</label>
                  <input
                    type="text"
                    name="campo"
                    value={formData.campo}
                    onChange={handleChange}
                    placeholder="Informação adicional (opcional)"
                  />
                </div>
                
                <div className="form-group">
                  <label>Quantidade (QTD) *</label>
                  <input
                    type="number"
                    name="qtd"
                    value={formData.qtd}
                    onChange={handleChange}
                    step="0.01"
                    min="0"
                    required
                  />
                </div>
                
                <button 
                  type="submit" 
                  className="btn-submit"
                  disabled={loading}
                >
                  {loading ? '💾 Salvando...' : '💾 Salvar Contagem'}
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Contagem;
