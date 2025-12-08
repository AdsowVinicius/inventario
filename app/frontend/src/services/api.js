import axios from 'axios';

const API_BASE_URL = 'http://10.200.10.57:8000';

// Tempo de inatividade para expirar sessão (30 minutos em milissegundos)
const SESSION_TIMEOUT = 30 * 60 * 1000;
const LAST_ACTIVITY_KEY = 'lastActivity';

// Funções de gerenciamento de sessão por inatividade
const sessionManager = {
  // Atualiza o timestamp da última atividade
  updateActivity: () => {
    localStorage.setItem(LAST_ACTIVITY_KEY, Date.now().toString());
  },
  
  // Verifica se a sessão expirou por inatividade
  isSessionExpired: () => {
    const lastActivity = localStorage.getItem(LAST_ACTIVITY_KEY);
    if (!lastActivity) return false;
    
    const elapsed = Date.now() - parseInt(lastActivity, 10);
    return elapsed > SESSION_TIMEOUT;
  },
  
  // Faz logout por inatividade
  expireSession: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem(LAST_ACTIVITY_KEY);
    alert('⏱️ Sua sessão expirou por inatividade (30 minutos). Faça login novamente.');
    window.location.href = '/';
  },
  
  // Limpa o timer de inatividade
  clearActivity: () => {
    localStorage.removeItem(LAST_ACTIVITY_KEY);
  },
  
  // Inicia o monitoramento de atividade
  startMonitoring: () => {
    // Atualiza atividade em eventos do usuário
    const events = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click'];
    
    const handleActivity = () => {
      if (localStorage.getItem('token')) {
        sessionManager.updateActivity();
      }
    };
    
    events.forEach(event => {
      document.addEventListener(event, handleActivity, { passive: true });
    });
    
    // Verifica periodicamente se a sessão expirou (a cada 1 minuto)
    setInterval(() => {
      if (localStorage.getItem('token') && sessionManager.isSessionExpired()) {
        sessionManager.expireSession();
      }
    }, 60 * 1000);
    
    // Inicializa o timestamp se logado
    if (localStorage.getItem('token')) {
      sessionManager.updateActivity();
    }
  }
};

// Iniciar monitoramento quando o script carregar
sessionManager.startMonitoring();

// Criar instância do axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token JWT
api.interceptors.request.use(
  (config) => {
    // Verificar se sessão expirou antes de cada requisição
    if (localStorage.getItem('token') && sessionManager.isSessionExpired()) {
      sessionManager.expireSession();
      return Promise.reject(new Error('Sessão expirada'));
    }
    
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      // Atualizar atividade em cada requisição
      sessionManager.updateActivity();
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para tratar erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token inválido ou expirado
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Serviços de autenticação
export const authService = {
  login: async (user_name, senha) => {
    const response = await api.post('/auth/login', { user_name, senha });
    // Iniciar controle de atividade após login
    sessionManager.updateActivity();
    return response.data;
  },
  
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    sessionManager.clearActivity();
  },
  
  getCurrentUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
  
  isAuthenticated: () => {
    // Verificar se tem token E se a sessão não expirou
    const hasToken = !!localStorage.getItem('token');
    if (hasToken && sessionManager.isSessionExpired()) {
      sessionManager.expireSession();
      return false;
    }
    return hasToken;
  },
  
  alterarSenha: async (senhaAtual, novaSenha, confirmarSenha) => {
    const response = await api.post('/auth/alterar-senha', {
      senha_atual: senhaAtual,
      nova_senha: novaSenha,
      confirmar_senha: confirmarSenha
    });
    return response.data;
  },
};

// Serviços de itens
export const itensService = {
  listar: async (planta, busca, skip = 0, limit = 50) => {
    const params = { skip, limit };
    if (planta) params.planta = planta;
    if (busca) params.busca = busca;
    const response = await api.get('/itens/', { params });
    return response.data;
  },
  
  contarTotal: async (planta, busca) => {
    const params = {};
    if (planta) params.planta = planta;
    if (busca) params.busca = busca;
    const response = await api.get('/itens/total', { params });
    return response.data;
  },
  
  obterPorId: async (id) => {
    const response = await api.get(`/itens/${id}`);
    return response.data;
  },
  
  criar: async (dados) => {
    const response = await api.post('/itens/', dados);
    return response.data;
  },
  
  atualizar: async (id, dados) => {
    const response = await api.put(`/itens/${id}`, dados);
    return response.data;
  },
  
  excluir: async (id) => {
    const response = await api.delete(`/itens/${id}`);
    return response.data;
  },
  
  listarPartNumbers: async (planta) => {
    const params = planta ? { planta } : {};
    const response = await api.get('/itens/part-numbers', { params });
    return response.data;
  },
  
  buscarPartNumbers: async (termo, planta) => {
    const params = { q: termo };
    if (planta) params.planta = planta;
    const response = await api.get('/itens/buscar', { params });
    return response.data;
  },
  
  obterDetalhes: async (partNumber, planta, silencioso = false) => {
    try {
      const params = planta ? { planta } : {};
      const response = await api.get(`/itens/detalhes/${encodeURIComponent(partNumber)}`, { params });
      return response.data;
    } catch (err) {
      // Se for 404 e modo silencioso, retorna null sem logar erro
      if (err.response?.status === 404) {
        if (!silencioso) {
          // Propaga o erro apenas se não for silencioso
          throw err;
        }
        return null;
      }
      // Outros erros sempre propagam
      throw err;
    }
  },
};

// Serviços de contagem
export const contagemService = {
  sugerirNumero: async (pn, etiqueta, planta) => {
    const params = { etiqueta, planta };
    if (pn !== undefined && pn !== null && pn !== '') {
      params.pn = pn;
    }
    const response = await api.get('/contagem/sugerir', { params });
    return response.data;
  },

  sugerir: async (pn, etiqueta, planta) => {
    return contagemService.sugerirNumero(pn, etiqueta, planta);
  },
  
  salvar: async (dados) => {
    const response = await api.post('/contagem/salvar', dados);
    return response.data;
  },
};

// Serviços de exportação
export const exportacaoService = {
  preview: async (filtros) => {
    const response = await api.get('/exportacao/preview', {
      params: filtros
    });
    return response.data;
  },
  
  exportarCSV: async (filtros) => {
    const response = await api.get('/exportacao/csv', {
      params: filtros,
      responseType: 'blob'
    });
    
    // Criar link para download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'contagens.csv');
    document.body.appendChild(link);
    link.click();
    link.remove();
  },
  
  exportarExcel: async (filtros) => {
    const response = await api.get('/exportacao/excel', {
      params: filtros,
      responseType: 'blob'
    });
    
    // Criar link para download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'contagens.xlsx');
    document.body.appendChild(link);
    link.click();
    link.remove();
  },
};

export default api;
