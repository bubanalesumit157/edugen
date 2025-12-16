import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const register = async (email: string, password: string, role: string) => {
  await axios.post(`${API_URL}/register`, { email, password, role });
};

export const login = async (email: string, password: string) => {
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);

  const response = await axios.post(`${API_URL}/token`, formData);
  localStorage.setItem('token', response.data.access_token);

  // Fetch user ID immediately after login
  const userRes = await axios.get(`${API_URL}/users/me`, {
    headers: { Authorization: `Bearer ${response.data.access_token}` }
  });
  localStorage.setItem('user', JSON.stringify(userRes.data));
};

export const getCurrentUser = () => {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
};

export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = '/login';
};