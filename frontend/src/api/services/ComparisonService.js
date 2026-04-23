import apiClient from '../client';
import { COMPARISONS_URL } from '../../constants/ApiUrls';

const ComparisonService = {
  async getComparisons() {
    try {
      const response = await apiClient.get(COMPARISONS_URL);
      return response.data;
    } catch (err) {
      console.error('Get comparisons error:', err);
      throw err;
    }
  },

  async getComparison(id) {
    try {
      const response = await apiClient.get(`${COMPARISONS_URL}${id}/`);
      return response.data;
    } catch (err) {
      console.error('Get comparison error:', err);
      throw err;
    }
  },

  async getComparisonDetail(id) {
    try {
      const response = await apiClient.get(`${COMPARISONS_URL}${id}/detail/`);
      return response.data;
    } catch (err) {
      console.error('Get comparison detail error:', err);
      throw err;
    }
  },

  async createComparison(name) {
    try {
      const response = await apiClient.post(COMPARISONS_URL, { name });
      return response.data;
    } catch (err) {
      console.error('Create comparison error:', err);
      throw err;
    }
  },

  async updateComparison(id, data) {
    try {
      const response = await apiClient.patch(`${COMPARISONS_URL}${id}/`, data);
      return response.data;
    } catch (err) {
      console.error('Update comparison error:', err);
      throw err;
    }
  },

  async deleteComparison(id) {
    try {
      await apiClient.delete(`${COMPARISONS_URL}${id}/`);
      return true;
    } catch (err) {
      console.error('Delete comparison error:', err);
      throw err;
    }
  },

  async addVacancy(comparisonId, vacancyId) {
    try {
      const response = await apiClient.post(
        `${COMPARISONS_URL}${comparisonId}/vacancies/${vacancyId}/`
      );
      return response.data;
    } catch (err) {
      console.error('Add vacancy to comparison error:', err);
      throw err;
    }
  },

  async removeVacancy(comparisonId, vacancyId) {
    try {
      const response = await apiClient.delete(
        `${COMPARISONS_URL}${comparisonId}/vacancies/${vacancyId}/`
      );
      return response.data;
    } catch (err) {
      console.error('Remove vacancy from comparison error:', err);
      throw err;
    }
  },

  async analyzeComparison(comparisonId) {
    try {
      const response = await apiClient.post(`${COMPARISONS_URL}${comparisonId}/analyze/`);
      return response.data;
    } catch (err) {
      console.error('Analyze comparison error:', err);
      throw err;
    }
  },
};

export default ComparisonService;
