import apiClient from '../client';
import { CURRENCIES_URL } from '../../constants/ApiUrls';

const CurrencyService = {
  async getAll() {
    try {
      const response = await apiClient.get(CURRENCIES_URL);
      return response.data;
    } catch (err) {
      console.error('Get currencies error:', err);
      throw err;
    }
  },
};

export default CurrencyService;
