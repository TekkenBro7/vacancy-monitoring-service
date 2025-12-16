import axios from 'axios';
import { HttpStatusCode } from 'axios';
import { AUTH_URL } from '@/constants/ApiUrls';

async function refreshToken() {
  try {
    const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}${AUTH_URL}refresh/`);
    const { access_token } = response.data;
    if (access_token) {
      localStorage.setItem('token', access_token);
      return access_token;
    }
  } catch (err) {
    localStorage.removeItem('token');
    throw err;
  }
}

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

apiClient.interceptors.request.use(
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

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === HttpStatusCode.Unauthorized && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        await refreshToken();
        return apiClient(originalRequest);
      } catch (err) {
        return Promise.reject(err);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
