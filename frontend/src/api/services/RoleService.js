import apiClient from '../client';
import { ROLES_URL } from '../../constants/ApiUrls';

export const RoleService = {
  async getAll() {
    try {
      const response = await apiClient.get(ROLES_URL);
      return response.data;
    } catch (err) {
      console.error('Get all roles error:', err);
      throw err;
    }
  },
};

export default RoleService;
