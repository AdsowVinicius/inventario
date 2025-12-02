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

const normalizeCode = (value) => {
  if (value === null || value === undefined) return '';
  const text = String(value).trim();
  if (text === '') return '';
  const sanitized = text.replace(/^0+/, '');
  return sanitized === '' ? '0' : sanitized;
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
    etiqueta_inventario: '',
    part_number: '',
    qtd: 0
  });
  
  const [partNumbers, setPartNumbers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [contagensRealizadas, setContagensRealizadas] = useState(0);
  const [zonasDisponiveis, setZonasDisponiveis] = useState(
    ZONAS_POR_PLANTA[user?.planta || 'PS01'] || []
  );
  const [numContagem, setNumContagem] = useState(1);
  const [numeroSugerido, setNumeroSugerido] = useState(1);
  const [contagemErrada, setContagemErrada] = useState(false);
  const [unidadeMedida, setUnidadeMedida] = useState('');
  const [buscandoSugestao, setBuscandoSugestao] = useState(false);
  const [sugestaoTrigger, setSugestaoTrigger] = useState(0);

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
      const enriquecidos = data.map(item => ({
        ...item,
        part_number_normalizado: normalizeCode(item.part_number)
      }));
      setPartNumbers(enriquecidos);
    } catch (err) {
      console.error('Erro ao carregar part numbers:', err);
    }
  };

  useEffect(() => {
    if (!formData.part_number) {
      setUnidadeMedida('');
      return;
    }

    const atualNormalizado = normalizeCode(formData.part_number);
    const info = partNumbers.find(item => 
      item.part_number === formData.part_number || item.part_number_normalizado === atualNormalizado
    );
    setUnidadeMedida(info?.und_medida || '');
  }, [formData.part_number, partNumbers]);
  
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
      etiqueta_inventario: '',
      part_number: '',
      qtd: 0
    });
    setMessage(null);
    setContagensRealizadas(0);
    setNumContagem(1);
    setNumeroSugerido(1);
    setContagemErrada(false);
    setUnidadeMedida('');
    setBuscandoSugestao(false);
    setSugestaoTrigger(0);
  };
  
  const handleZonaChange = (e) => {
    const { name, value } = e.target;
    setZonaAtual(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  // Número de contagem é gerado automaticamente pelo backend

  useEffect(() => {
    if (etapa !== 2) {
      setNumeroSugerido(1);
      setBuscandoSugestao(false);
      if (!contagemErrada) {
        setNumContagem(1);
      }
      return;
    }

    if (!formData.etiqueta_inventario) {
      setNumeroSugerido(1);
      setBuscandoSugestao(false);
      if (!contagemErrada) {
        setNumContagem(1);
      }
      return;
    }

    let ativo = true;
    setBuscandoSugestao(true);

    contagemService.sugerir(
      formData.part_number ? normalizeCode(formData.part_number) : undefined,
      normalizeCode(formData.etiqueta_inventario),
      zonaAtual.planta || plantaUsuario
    ).then((data) => {
      if (!ativo) return;
      setNumeroSugerido(data.num_contagem_sugerido);
      if (!contagemErrada) {
        setNumContagem(data.num_contagem_sugerido);
      }
    }).catch((err) => {
      if (!ativo) return;
      console.error('Erro ao sugerir número de contagem:', err);
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Erro ao sugerir número da contagem'
      });
    }).finally(() => {
      if (ativo) {
        setBuscandoSugestao(false);
      }
    });

    return () => {
      ativo = false;
    };
  }, [etapa, formData.part_number, formData.etiqueta_inventario, zonaAtual.planta, contagemErrada, plantaUsuario, sugestaoTrigger]);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'qtd' ? parseFloat(value) || 0 : value
    }));
    setMessage(null);
  };

  const handleNumeroContagemChange = (value) => {
    const parsed = parseInt(value, 10);
    if (Number.isNaN(parsed) || parsed < 1) {
      setNumContagem(1);
      return;
    }
    setNumContagem(parsed);
  };

  const handleContagemErradaChange = (e) => {
    const { checked } = e.target;
    setContagemErrada(checked);
    if (!checked) {
      setNumContagem(numeroSugerido);
    }
  };

  const handleEtiquetaBlur = () => {
    if (!formData.etiqueta_inventario) {
      return;
    }
    const normalizada = normalizeCode(formData.etiqueta_inventario);
    setFormData(prev => ({
      ...prev,
      etiqueta_inventario: normalizada
    }));
    setSugestaoTrigger(prev => prev + 1);
  };

  const handlePartNumberBlur = () => {
    if (!formData.part_number) {
      return;
    }
    const normalizada = normalizeCode(formData.part_number);
    setFormData(prev => ({
      ...prev,
      part_number: normalizada
    }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    
    try {
      // Combinar dados da zona com dados da contagem
      const dadosCompletos = {
        ...zonaAtual,
        ...formData,
        etiqueta_inventario: normalizeCode(formData.etiqueta_inventario) || formData.etiqueta_inventario,
        part_number: formData.part_number ? (normalizeCode(formData.part_number) || formData.part_number) : '',
        ...(contagemErrada ? { num_contagem: numContagem } : {})
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
        etiqueta_inventario: '',
        part_number: '',
        qtd: 0
      });
      setContagemErrada(false);
      setNumContagem(1);
      setNumeroSugerido(1);
      setUnidadeMedida('');
      setSugestaoTrigger(prev => prev + 1);
      
      // Focar no primeiro campo
      setTimeout(() => {
        document.querySelector('input[name="etiqueta_inventario"]')?.focus();
      }, 100);
      
      // Limpar mensagem após 3 segundos
      setTimeout(() => setMessage(null), 3000);
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Erro ao salvar contagem'
      });
      
      // Manter mensagem de erro por mais tempo (5 segundos)
      setTimeout(() => setMessage(null), 5000);
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
                    <label>Etiqueta de Inventário *</label>
                    <input
                      type="number"
                      name="etiqueta_inventario"
                      value={formData.etiqueta_inventario}
                      onChange={handleChange}
                      onBlur={handleEtiquetaBlur}
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
                    onBlur={handlePartNumberBlur}
                    placeholder="Digite ou escaneie o código numérico"
                    required
                    min="0"
                    step="1"
                  />
                </div>
                
                <div className="form-row contagem-numero-row">
                  <div className="form-group">
                    <label>Número da Contagem</label>
                    <div className="contagem-numero-wrapper">
                      <input
                        type="number"
                        name="num_contagem"
                        value={numContagem}
                        onChange={(e) => handleNumeroContagemChange(e.target.value)}
                        min="1"
                        step="1"
                        disabled={!contagemErrada}
                      />
                      <span className="sugestao-badge">
                        {buscandoSugestao ? 'Buscando...' : `Sugestão: #${numeroSugerido}`}
                      </span>
                    </div>
                    <small className="help-text">
                      {contagemErrada ? 'Valor editável para corrigir divergências' : 'Preenchido automaticamente pelo sistema'}
                    </small>
                  </div>
                  <div className="form-group checkbox-group">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={contagemErrada}
                        onChange={handleContagemErradaChange}
                      />
                      Corrigir contagem
                    </label>
                    <small className="help-text">
                      Permite ajustar o número manualmente
                    </small>
                  </div>
                </div>
                
                <div className="form-group">
                  <label>
                    Quantidade (QTD) *
                    {unidadeMedida && (
                      <span className="unit-tag">{unidadeMedida}</span>
                    )}
                  </label>
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
