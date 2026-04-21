import apiClient from '../client';
import { CITIES_URL } from '../../constants/ApiUrls';

const CityService = {
  async getAll() {
    try {
      const response = await apiClient.get(CITIES_URL);
      return response.data;
    } catch (err) {
      console.error('Get cities error:', err);
      throw err;
    }
  },
};

export default CityService;
