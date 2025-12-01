import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

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
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
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
    return response.data;
  },
  
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
  
  getCurrentUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
  
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },
};

// Serviços de itens
export const itensService = {
  listarPartNumbers: async (planta) => {
    const params = planta ? { planta } : {};
    const response = await api.get('/itens/part-numbers', { params });
    return response.data;
  },
};

// Serviços de contagem
export const contagemService = {
  sugerirNumero: async (pn, etiqueta, planta) => {
    const response = await api.get('/contagem/sugerir', {
      params: { pn, etiqueta, planta }
    });
    return response.data;
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
