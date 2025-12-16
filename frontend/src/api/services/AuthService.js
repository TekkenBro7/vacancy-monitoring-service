import apiClient from '../client';
import { AUTH_URL } from '../../constants/ApiUrls';

const AuthService = {
  async login(data) {
    try {
      const response = await apiClient.post(`${AUTH_URL}login/`, data);
      const { access_token } = response.data;

      if (access_token) {
        localStorage.setItem('token', access_token);

        const user = await this.fetchCurrentUser();
        if (user) {
          localStorage.setItem('user', JSON.stringify(user));
        }
      }
    } catch (err) {
      console.error('Login error:', err);
      throw err;
    }
  },

  async fetchCurrentUser() {
    try {
      const response = await apiClient.get(`${AUTH_URL}users/me/`);
      return response.data;
    } catch {
      return null;
    }
  },

  async refresh() {
    try {
      const response = await apiClient.post(`${AUTH_URL}refresh/`);

      const { access_token } = response.data;

      if (access_token) {
        localStorage.setItem('token', access_token);

        return response;
      }
    } catch (err) {
      this.logout();
      throw err;
    }
  },

  async logout() {
    try {
      await apiClient.post(`${AUTH_URL}logout/`);
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  },

  isAuthenticated() {
    return !!localStorage.getItem('token');
  },
};

export default AuthService;
