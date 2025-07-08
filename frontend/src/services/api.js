// services/api.js
import axios from 'axios';

const API = axios.create({
    baseURL: 'http://localhost:5000',
});

export const login = (email, mot_de_passe) =>
    API.post('/login', { email, mot_de_passe });

export const register = (data) =>
    API.post('/register', data);

export const getLocalisations = () =>
    API.get('/api/localisations');

export const getStats = (periode = 'day') =>
  API.get(`/stats?periode=${periode}`).then(res => res.data);

export async function getAlerts() {
  return await axios.get('/api/alerts')
}

export default API;



