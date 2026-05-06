import axios from 'react'; // Ignore this, actually importing axios properly below
import axiosInstance from 'axios';

const api = axiosInstance.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getFundamental = async (ticker) => {
  try {
    const response = await api.get(`/api/fundamental/${ticker}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || `Failed to fetch fundamental data for ${ticker}`);
  }
};

export const getStatements = async (ticker) => {
  try {
    const response = await api.get(`/api/fundamental/${ticker}/statements`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || `Failed to fetch statements for ${ticker}`);
  }
};

export const runClustering = async (body) => {
  try {
    const response = await api.post('/api/patterns/cluster', body);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Clustering failed');
  }
};

export const runAssociation = async (body) => {
  try {
    const response = await api.post('/api/patterns/association', body);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Association rules mining failed');
  }
};

export const getAnomalies = async (ticker, period) => {
  try {
    const response = await api.get(`/api/patterns/anomalies/${ticker}?period=${period}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Anomaly detection failed');
  }
};

export const getStrategies = async () => {
  try {
    const response = await api.get('/api/backtest/strategies');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch strategies');
  }
};

export const runBacktest = async (body) => {
  try {
    const response = await api.post('/api/backtest/run', body);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Backtest failed');
  }
};
