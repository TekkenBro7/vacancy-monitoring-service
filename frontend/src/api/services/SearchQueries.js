import apiClient from '../client';
import { SEARCH_QUERIES_URL } from '../../constants/ApiUrls';

export const SearchQueriesService = {
  getUserQueries: async (userId) => {
    const response = await apiClient.get(`${SEARCH_QUERIES_URL}user/${userId}/`);
    return response.data;
  },

  createQuery: async (userId, queryText) => {
    const response = await apiClient.post(`${SEARCH_QUERIES_URL}`, {
      user_id: userId,
      query_text: queryText,
    });
    return response.data;
  },

  deleteQuery: async (queryId) => {
    const response = await apiClient.delete(`${SEARCH_QUERIES_URL}${queryId}/`);
    return response.data;
  },
};
