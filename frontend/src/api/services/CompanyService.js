import apiClient from '../client';
import { COMPANIES_URL } from '../../constants/ApiUrls';

const CompanyService = {
  async getAll() {
    try {
      const response = await apiClient.get(COMPANIES_URL);
      return response.data;
    } catch (err) {
      console.error('Get companies error:', err);
      throw err;
    }
  },
};

export default CompanyService;
