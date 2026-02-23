import apiClient from '../client';
import { SKILLS_URL } from '../../constants/ApiUrls';

export const SkillService = {
  async getAll() {
    try {
      const response = await apiClient.get(SKILLS_URL);
      return response.data;
    } catch (err) {
      console.error('Get all skills error:', err);
      throw err;
    }
  },

  async create(data) {
    try {
      const response = await apiClient.post(SKILLS_URL, data);
      return response.data;
    } catch (err) {
      console.error('Create skill error:', err);
      throw err;
    }
  },

  async update(skillId, data) {
    try {
      const response = await apiClient.patch(`${SKILLS_URL}${skillId}/`, data);
      return response.data;
    } catch (err) {
      console.error('Update skill error:', err);
      throw err;
    }
  },

  async delete(skillId) {
    try {
      const response = await apiClient.delete(`${SKILLS_URL}${skillId}/`);
      return response.data;
    } catch (err) {
      console.error('Delete skill error:', err);
      throw err;
    }
  },
};

export default SkillService;
