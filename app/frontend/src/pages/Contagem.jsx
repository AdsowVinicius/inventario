import React, { useState, useEffect, useRef } from 'react';
import { authService, itensService, contagemService } from '../services/api';
import Navbar from '../components/Navbar';
import './Contagem.css';

const PLANTAS = ['PS01', 'PS02', 'PS03', 'PS05', 'PB82'];

// Zonas específicas por planta
const ZONAS_POR_PLANTA = {
  'PS01': [
    { codigo: 'A', descricao: 'Acabado' },
    { codigo: 'B', descricao: 'Semi-Acabado' },
    { codigo: 'C', descricao: 'Matéria-Prima/Embalagens' },
    { codigo: 'D', descricao: 'Almoxarifado' },
    { codigo: 'E', descricao: 'Câmara-Fria' },
    { codigo: 'F', descricao: 'Qualidade' },
    { codigo: 'G', descricao: 'Engenharia' }
  ],
  'PS02': [
    { codigo: 'A', descricao: 'G2' },
    { codigo: 'B', descricao: 'Qualidade' },
    { codigo: 'C', descricao: 'Sala de Tintas' },
    { codigo: 'D', descricao: 'Almoxarifado de Tintas' },
    { codigo: 'E', descricao: 'Almoxarifado' },
    { codigo: 'F', descricao: 'Almox/Manutenção' },
    { codigo: 'G', descricao: 'Polimento/Retoque' },
    { codigo: 'H', descricao: 'Montagem' },
    { codigo: 'I', descricao: 'Estoque Acabado' }
  ],
  'PS03': [
    { codigo: 'A', descricao: 'Acabado' },
    { codigo: 'B', descricao: 'Semi-Acabado' },
    { codigo: 'C', descricao: 'Componentes/Embalagens' },
    { codigo: 'D', descricao: 'Sala de Tintas' },
    { codigo: 'E', descricao: 'Almoxarifado' }
  ],
  'PS05': [
    { codigo: 'A', descricao: 'Almoxarifado' },
    { codigo: 'B', descricao: 'Estoque Acabado' },
    { codigo: 'C', descricao: 'Montagem' },
    { codigo: 'D', descricao: 'Colagem' },
    { codigo: 'E', descricao: 'Semi-Acabado' },
    { codigo: 'F', descricao: 'Sala de Materiais' },
    { codigo: 'G', descricao: 'G2' },
    { codigo: 'H', descricao: 'Obsoleto' },
    { codigo: 'I', descricao: 'Engenharia/Qualidade' }
  ],
  'PB82': [
    { codigo: 'A', descricao: 'Almoxarifado' },
    { codigo: 'B', descricao: 'Estoque' },
    { codigo: 'C', descricao: 'Produção' }
  ]
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
  
  // Contagem selecionada pelo usuário (1, 2 ou 3) - escolhida na etapa 1
  const [contagemSelecionada, setContagemSelecionada] = useState(1);
  
  const [formData, setFormData] = useState({
    etiqueta_inventario: '',
    part_number: '',
    qtd: ''
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
  const [limiteAtingido, setLimiteAtingido] = useState(false);
  
  // Histórico de contagens realizadas na sessão
  const [historicoContagens, setHistoricoContagens] = useState([]);
  
  // Estados para autocomplete do Part Number
  const [sugestoesPn, setSugestoesPn] = useState([]);
  const [mostrarSugestoes, setMostrarSugestoes] = useState(false);
  const [buscandoPn, setBuscandoPn] = useState(false);
  const [itemSelecionado, setItemSelecionado] = useState(null);
  const [indiceSugestao, setIndiceSugestao] = useState(-1);
  const [pnNaoEncontrado, setPnNaoEncontrado] = useState(false);
  const inputPnRef = useRef(null);
  const sugestoesRef = useRef(null);
  const debounceRef = useRef(null);

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

  // Buscar part numbers conforme usuário digita
  const buscarPartNumbers = async (termo) => {
    if (!termo || termo.length < 1) {
      setSugestoesPn([]);
      setMostrarSugestoes(false);
      return;
    }
    
    setBuscandoPn(true);
    try {
      const resultados = await itensService.buscarPartNumbers(termo, plantaUsuario);
      setSugestoesPn(resultados);
      setMostrarSugestoes(resultados.length > 0);
      setIndiceSugestao(-1);
    } catch (err) {
      console.error('Erro ao buscar part numbers:', err);
      setSugestoesPn([]);
    } finally {
      setBuscandoPn(false);
    }
  };

  // Buscar detalhes do item quando part number é definido (por scan ou seleção)
  const buscarDetalhesItem = async (partNumber) => {
    if (!partNumber) {
      setItemSelecionado(null);
      setUnidadeMedida('');
      return;
    }
    
    try {
      const detalhes = await itensService.obterDetalhes(partNumber, plantaUsuario);
      if (detalhes) {
        setItemSelecionado(detalhes);
        setUnidadeMedida(detalhes.und_medida || '');
      }
    } catch (err) {
      console.error('Erro ao buscar detalhes:', err);
      // Tentar buscar localmente
      const atualNormalizado = normalizeCode(partNumber);
      const info = partNumbers.find(item => 
        item.part_number === partNumber || item.part_number_normalizado === atualNormalizado
      );
      if (info) {
        setItemSelecionado(info);
        setUnidadeMedida(info.und_medida || '');
      }
    }
  };

  useEffect(() => {
    if (!formData.part_number) {
      setUnidadeMedida('');
      setItemSelecionado(null);
      return;
    }

    // Buscar detalhes quando part number muda (após seleção ou scan)
    if (!mostrarSugestoes) {
      buscarDetalhesItem(formData.part_number);
    }
  }, [formData.part_number, mostrarSugestoes]);
  
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
      qtd: ''
    });
    setMessage(null);
    setContagensRealizadas(0);
    setContagemSelecionada(1);
    setNumContagem(1);
    setNumeroSugerido(1);
    setContagemErrada(false);
    setUnidadeMedida('');
    setBuscandoSugestao(false);
    setSugestaoTrigger(0);
    setItemSelecionado(null);
    setSugestoesPn([]);
    setMostrarSugestoes(false);
    setPnNaoEncontrado(false);
    setLimiteAtingido(false);
    setHistoricoContagens([]);
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
      setLimiteAtingido(false);
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
      setLimiteAtingido(data.limite_atingido || false);
      if (!contagemErrada) {
        setNumContagem(data.num_contagem_sugerido);
      }
      // Mostrar aviso se limite atingido
      if (data.limite_atingido) {
        setMessage({
          type: 'error',
          text: `⚠️ Limite atingido! Esta etiqueta já foi contada 3 vezes. Não é possível realizar outra contagem.`
        });
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
      [name]: value
    }));
    setMessage(null);
  };
  
  // Handler especial para etiqueta - aceita apenas números (máx 5 dígitos)
  const handleEtiquetaChange = (e) => {
    const value = e.target.value;
    // Permite apenas números e limita a 5 dígitos
    const sanitized = value.replace(/[^0-9]/g, '').slice(0, 5);
    setFormData(prev => ({
      ...prev,
      etiqueta_inventario: sanitized
    }));
    setMessage(null);
    setLimiteAtingido(false);
  };
  
  // Handler especial para quantidade - aceita apenas números
  const handleQtdChange = (e) => {
    const value = e.target.value;
    // Permite apenas números, ponto e vírgula (para decimais)
    const sanitized = value.replace(/[^0-9.,]/g, '').replace(',', '.');
    setFormData(prev => ({
      ...prev,
      qtd: sanitized
    }));
    setMessage(null);
  };
  
  // Handler especial para Part Number com debounce
  const handlePartNumberChange = (e) => {
    const { value } = e.target;
    setFormData(prev => ({
      ...prev,
      part_number: value
    }));
    setMessage(null);
    setItemSelecionado(null);
    setPnNaoEncontrado(false);
    
    // Debounce para busca
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }
    
    debounceRef.current = setTimeout(() => {
      buscarPartNumbers(value);
    }, 300);
  };
  
  // Selecionar item da lista de sugestões
  const selecionarItem = (item) => {
    setFormData(prev => ({
      ...prev,
      part_number: item.part_number
    }));
    setItemSelecionado(item);
    setUnidadeMedida(item.und_medida || '');
    setSugestoesPn([]);
    setMostrarSugestoes(false);
    setIndiceSugestao(-1);
    setPnNaoEncontrado(false);
    setMessage(null);
    
    // Focar no campo quantidade
    setTimeout(() => {
      document.querySelector('input[name="qtd"]')?.focus();
    }, 100);
  };
  
  // Navegação por teclado nas sugestões
  const handlePartNumberKeyDown = (e) => {
    if (!mostrarSugestoes || sugestoesPn.length === 0) {
      return;
    }
    
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setIndiceSugestao(prev => 
          prev < sugestoesPn.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setIndiceSugestao(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        if (indiceSugestao >= 0 && indiceSugestao < sugestoesPn.length) {
          e.preventDefault();
          selecionarItem(sugestoesPn[indiceSugestao]);
        }
        break;
      case 'Escape':
        setMostrarSugestoes(false);
        setIndiceSugestao(-1);
        break;
      default:
        break;
    }
  };
  
  // Fechar sugestões ao clicar fora
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (
        sugestoesRef.current && 
        !sugestoesRef.current.contains(e.target) &&
        inputPnRef.current &&
        !inputPnRef.current.contains(e.target)
      ) {
        setMostrarSugestoes(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

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

  const handlePartNumberBlur = async () => {
    // Fechar sugestões com delay para permitir clique
    setTimeout(() => {
      setMostrarSugestoes(false);
    }, 200);
    
    // Se não tem part number, limpar estado
    if (!formData.part_number) {
      setPnNaoEncontrado(false);
      setItemSelecionado(null);
      return;
    }
    
    // Se já tem um item selecionado (veio do autocomplete), não fazer nova busca
    if (itemSelecionado && itemSelecionado.part_number === formData.part_number) {
      setPnNaoEncontrado(false);
      return;
    }
    
    const normalizada = normalizeCode(formData.part_number);
    setFormData(prev => ({
      ...prev,
      part_number: normalizada
    }));
    
    // Buscar detalhes após normalização e verificar se existe
    try {
      const detalhes = await itensService.obterDetalhes(normalizada, plantaUsuario);
      // Se chegou aqui, encontrou o item
      if (detalhes && detalhes.part_number) {
        setItemSelecionado(detalhes);
        setUnidadeMedida(detalhes.und_medida || '');
        setPnNaoEncontrado(false);
        setMessage(null);
      }
    } catch (err) {
      // 404 = não encontrado
      if (err.response?.status === 404) {
        setItemSelecionado(null);
        setPnNaoEncontrado(true);
        setMessage({
          type: 'error',
          text: `Part Number "${normalizada}" não cadastrado. Solicite o cadastro ao Gestor, Controladoria ou Administrador.`
        });
      } else {
        // Outro erro - pode ser rede, etc
        console.error('Erro ao buscar detalhes:', err);
      }
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Bloquear se limite de contagens atingido
    if (limiteAtingido) {
      setMessage({
        type: 'error',
        text: '⚠️ Limite atingido! Esta etiqueta já foi contada 3 vezes. Não é possível realizar outra contagem.'
      });
      return;
    }
    
    // Bloquear se Part Number não encontrado
    if (pnNaoEncontrado || !itemSelecionado) {
      setMessage({
        type: 'error',
        text: 'Part Number não cadastrado no sistema. Solicite o cadastro ao Gestor, Controladoria ou Administrador.'
      });
      return;
    }
    
    // Validar quantidade
    const qtdNum = parseFloat(formData.qtd);
    if (isNaN(qtdNum) || qtdNum < 0) {
      setMessage({
        type: 'error',
        text: 'Quantidade inválida. Digite um número válido.'
      });
      return;
    }
    
    setLoading(true);
    setMessage(null);
    
    try {
      // Combinar dados da zona com dados da contagem
      // Sempre envia o num_contagem selecionado pelo usuário
      const dadosCompletos = {
        ...zonaAtual,
        ...formData,
        qtd: qtdNum,
        etiqueta_inventario: normalizeCode(formData.etiqueta_inventario) || formData.etiqueta_inventario,
        part_number: formData.part_number ? (normalizeCode(formData.part_number) || formData.part_number) : '',
        num_contagem: contagemSelecionada
      };
      
      const response = await contagemService.salvar(dadosCompletos);
      
      // Adicionar ao histórico
      setHistoricoContagens(prev => [{
        id: Date.now(),
        etiqueta: dadosCompletos.etiqueta_inventario,
        part_number: dadosCompletos.part_number,
        descricao: itemSelecionado?.descricao || '',
        num_contagem: contagemSelecionada,
        timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
      }, ...prev]);
      
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
        qtd: ''
      });
      setContagemErrada(false);
      setNumContagem(1);
      setNumeroSugerido(1);
      setUnidadeMedida('');
      setSugestaoTrigger(prev => prev + 1);
      setItemSelecionado(null);
      setSugestoesPn([]);
      setMostrarSugestoes(false);
      setPnNaoEncontrado(false);
      setLimiteAtingido(false);
      
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
            // ETAPA 1: Selecionar Zona e Contagem
            <>
              <h2>📍 Etapa 1: Selecionar Zona e Contagem</h2>
              <p className="subtitle">Sua planta: <strong>{plantaUsuario}</strong> - Selecione a zona e qual contagem você irá realizar</p>
              
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
                      <option key={zona.codigo} value={zona.codigo}>
                        {zona.codigo} - {zona.descricao}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Qual contagem você irá realizar? *</label>
                  <div className="contagem-selection-buttons">
                    <button
                      type="button"
                      className={`contagem-select-btn ${contagemSelecionada === 1 ? 'selected' : ''}`}
                      onClick={() => setContagemSelecionada(1)}
                    >
                      1ª Contagem
                    </button>
                    <button
                      type="button"
                      className={`contagem-select-btn ${contagemSelecionada === 2 ? 'selected' : ''}`}
                      onClick={() => setContagemSelecionada(2)}
                    >
                      2ª Contagem
                    </button>
                    <button
                      type="button"
                      className={`contagem-select-btn ${contagemSelecionada === 3 ? 'selected' : ''}`}
                      onClick={() => setContagemSelecionada(3)}
                    >
                      3ª Contagem
                    </button>
                  </div>
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
                  <h2>📝 Realizando {contagemSelecionada}ª Contagem</h2>
                  <div className="zona-badge">
                    <strong>Planta:</strong> {zonaAtual.planta} | <strong>Zona:</strong> {zonaAtual.zona_inventario} - {zonasDisponiveis.find(z => z.codigo === zonaAtual.zona_inventario)?.descricao || ''} | <strong className="contagem-badge">Contagem {contagemSelecionada}</strong>
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
                      type="text"
                      name="etiqueta_inventario"
                      value={formData.etiqueta_inventario}
                      onChange={handleEtiquetaChange}
                      onBlur={handleEtiquetaBlur}
                      placeholder="Ex: 12345"
                      required
                      maxLength={5}
                      inputMode="numeric"
                      pattern="[0-9]*"
                      autoFocus
                    />
                  </div>
                </div>
                
                <div className="form-group part-number-group">
                  <label>Part Number (Código de Barras) *</label>
                  <div className="autocomplete-container">
                    <input
                      ref={inputPnRef}
                      type="text"
                      name="part_number"
                      value={formData.part_number}
                      onChange={handlePartNumberChange}
                      onBlur={handlePartNumberBlur}
                      onKeyDown={handlePartNumberKeyDown}
                      onFocus={() => formData.part_number && sugestoesPn.length > 0 && setMostrarSugestoes(true)}
                      placeholder="Digite, pesquise ou escaneie o código"
                      required
                      autoComplete="off"
                    />
                    {buscandoPn && (
                      <span className="autocomplete-loading">🔍</span>
                    )}
                    
                    {mostrarSugestoes && sugestoesPn.length > 0 && (
                      <ul className="autocomplete-list" ref={sugestoesRef}>
                        {sugestoesPn.map((item, index) => (
                          <li 
                            key={item.part_number}
                            className={`autocomplete-item ${index === indiceSugestao ? 'active' : ''}`}
                            onMouseDown={(e) => {
                              e.preventDefault();
                              selecionarItem(item);
                            }}
                          >
                            <span className="pn-code">{item.part_number}</span>
                            <span className="pn-desc">{item.descricao || 'Sem descrição'}</span>
                            {item.und_medida && (
                              <span className="pn-unit">{item.und_medida}</span>
                            )}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                  
                  {/* Card de informações do item selecionado */}
                  {itemSelecionado && (
                    <div className="item-info-card">
                      <div className="item-info-header">
                        <span className="item-info-icon">📦</span>
                        <span className="item-info-title">Informações do Item</span>
                      </div>
                      <div className="item-info-body">
                        <div className="item-info-row">
                          <span className="item-info-label">Part Number:</span>
                          <span className="item-info-value">{itemSelecionado.part_number}</span>
                        </div>
                        <div className="item-info-row">
                          <span className="item-info-label">Descrição:</span>
                          <span className="item-info-value desc">{itemSelecionado.descricao || 'Não informada'}</span>
                        </div>
                        {itemSelecionado.und_medida && (
                          <div className="item-info-row">
                            <span className="item-info-label">Unidade:</span>
                            <span className="item-info-value">{itemSelecionado.und_medida}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {/* Alerta de Part Number não encontrado */}
                  {pnNaoEncontrado && (
                    <div className="pn-erro-card">
                      <span className="pn-erro-icon">⚠️</span>
                      <span className="pn-erro-text">
                        Part Number não cadastrado. Solicite o cadastro ao Gestor, Controladoria ou Administrador.
                      </span>
                    </div>
                  )}
                </div>
                
                <div className="form-group qtd-field">
                  <label>
                    Quantidade *
                    {unidadeMedida && <span className="unit-tag">{unidadeMedida}</span>}
                  </label>
                  <input
                    type="text"
                    name="qtd"
                    value={formData.qtd}
                    onChange={handleQtdChange}
                    placeholder="0"
                    inputMode="decimal"
                    pattern="[0-9]*[.,]?[0-9]*"
                    required
                  />
                </div>
                
                <button 
                  type="submit" 
                  className="btn-submit"
                  disabled={loading || pnNaoEncontrado || limiteAtingido}
                >
                  {loading ? '💾 Salvando...' : limiteAtingido ? '🚫 Limite Atingido (3x)' : '💾 Salvar Contagem'}
                </button>
              </form>
              
              {/* Histórico de Contagens */}
              {historicoContagens.length > 0 && (
                <div className="historico-contagens">
                  <h3 className="historico-titulo">
                    📋 Histórico da Sessão
                    <span className="historico-count">{historicoContagens.length}</span>
                  </h3>
                  <div className="historico-tabela-container">
                    <table className="historico-tabela">
                      <thead>
                        <tr>
                          <th>Hora</th>
                          <th>Etiqueta</th>
                          <th>Nº Cont.</th>
                          <th>Part Number</th>
                          <th className="desc-col">Descrição</th>
                        </tr>
                      </thead>
                      <tbody>
                        {historicoContagens.map((item) => (
                          <tr key={item.id}>
                            <td className="col-hora">{item.timestamp}</td>
                            <td className="col-etiqueta">{item.etiqueta}</td>
                            <td className="col-num">{item.num_contagem}</td>
                            <td className="col-pn">{item.part_number}</td>
                            <td className="col-desc">{item.descricao || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Contagem;
