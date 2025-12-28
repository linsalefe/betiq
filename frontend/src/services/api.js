import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Oportunidades
export const getOpportunities = async (bankroll) => {
  const response = await api.post('/opportunities', { bankroll });
  return response.data;
};

// Estatísticas
export const getStatistics = async () => {
  const response = await api.get('/statistics');
  return response.data;
};

// Histórico
export const getHistory = async (limit = 10) => {
  const response = await api.get(`/history?limit=${limit}`);
  return response.data;
};

// Registrar aposta
export const registerBet = async (betData) => {
  const response = await api.post('/register-bet', betData);
  return response.data;
};

// Chat com LLM
export const sendChatMessage = async (message, context = null) => {
  const response = await api.post('/chat', { message, context });
  return response.data;
};

// Fase atual
export const getCurrentPhase = async () => {
  const response = await api.get('/phase');
  return response.data;
};

export default api;