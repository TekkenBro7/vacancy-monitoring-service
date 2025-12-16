import apiClient from '../client';
import { USERS_URL } from '../../constants/ApiUrls';

export const UserService = {
  async getAll() {
    try {
      const response = await apiClient.get(USERS_URL);
      return response.data;
    } catch (err) {
      console.error('Get all error:', err);
      throw err;
    }
  },

  async getById(userId) {
    try {
      const response = await apiClient.get(`${USERS_URL}${userId}/`);
      return response.data;
    } catch (err) {
      console.error('Get by id error:', err);
      throw err;
    }
  },

  async create(data) {
    try {
      const response = await apiClient.post(USERS_URL, data);
      return response.data;
    } catch (err) {
      console.error('Create error:', err);
      throw err;
    }
  },

  async update(userId, data) {
    try {
      const response = await apiClient.patch(`${USERS_URL}${userId}/`, data);
      return response.data;
    } catch (err) {
      console.error('Update error:', err);
      throw err;
    }
  },

  async delete(userId) {
    try {
      const response = await apiClient.delete(`${USERS_URL}${userId}/`);
      return response.data;
    } catch (err) {
      console.error('Delete error:', err);
      throw err;
    }
  },
};
