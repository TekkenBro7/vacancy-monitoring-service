import apiClient from '../client';
import { VACANCIES_URL } from '../../constants/ApiUrls';

const VacancyService = {
  async getVacancies(params = {}) {
    try {
      const response = await apiClient.get(VACANCIES_URL, { params });
      return response.data;
    } catch (err) {
      console.error('Get vacancies error:', err);
      throw err;
    }
  },

  async getVacancyById(id) {
    try {
      const response = await apiClient.get(`${VACANCIES_URL}${id}/`);
      return response.data;
    } catch (err) {
      console.error('Get vacancy by id error:', err);
      throw err;
    }
  },

  async getVacancy(id) {
    try {
      const response = await apiClient.get(`${VACANCIES_URL}${id}/`);
      return response.data;
    } catch (err) {
      console.error('Get vacancy error:', err);
      throw err;
    }
  },

  async createVacancy(data) {
    try {
      const response = await apiClient.post(VACANCIES_URL, data);
      return response.data;
    } catch (err) {
      console.error('Create vacancy error:', err);
      throw err;
    }
  },

  async searchVacancies(params = {}) {
    try {
      const searchParams = new URLSearchParams();

      Object.entries(params).forEach(([key, value]) => {
        if (value === null || value === undefined || value === '') {
          return;
        }

        if (Array.isArray(value)) {
          value.forEach((item) => {
            if (item !== null && item !== undefined) {
              searchParams.append(key, item);
            }
          });
        } else {
          searchParams.append(key, value);
        }
      });

      const response = await apiClient.get(`${VACANCIES_URL}search?${searchParams.toString()}`);
      return response.data;
    } catch (err) {
      console.error('Search vacancies error:', err);
      throw err;
    }
  },

  async searchFilterOptions(filterType, query, params = {}) {
    try {
      const searchParams = new URLSearchParams();
      searchParams.append('filter_type', filterType);
      searchParams.append('query', query || '');
      searchParams.append('limit', '50');

      if (params.source_ids) {
        params.source_ids.forEach((id) => searchParams.append('source_ids', id));
      }

      const response = await apiClient.get(
        `${VACANCIES_URL}filters/search?${searchParams.toString()}`
      );
      return response.data;
    } catch (err) {
      console.error('Search filter options error:', err);
      throw err;
    }
  },

  async updateVacancy(id, data) {
    try {
      const response = await apiClient.patch(`${VACANCIES_URL}${id}/`, data);
      return response.data;
    } catch (err) {
      console.error('Update vacancy error:', err);
      throw err;
    }
  },

  async getAvailableFilters() {
    try {
      const response = await apiClient.get(`${VACANCIES_URL}filters/`);
      return response.data;
    } catch (err) {
      console.error('Get available filters error:', err);
      throw err;
    }
  },

  async deleteVacancy(id) {
    try {
      const response = await apiClient.delete(`${VACANCIES_URL}${id}/`);
      return response.data;
    } catch (err) {
      console.error('Delete vacancy error:', err);
      throw err;
    }
  },
};

export default VacancyService;
