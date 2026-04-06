import apiClient from '../client';
import { COMMENTS_URL } from '../../constants/ApiUrls';

const CommentService = {
  async getVacancyComments(vacancyId) {
    try {
      const response = await apiClient.get(`${COMMENTS_URL}vacancy/${vacancyId}/`);
      return response.data;
    } catch (err) {
      console.error('Get comments error:', err);
      throw err;
    }
  },

  async getVacancyStats(vacancyId) {
    try {
      const response = await apiClient.get(`${COMMENTS_URL}vacancy/${vacancyId}/stats/`);
      return response.data;
    } catch (err) {
      console.error('Get comment stats error:', err);
      throw err;
    }
  },

  async createComment(vacancyId, content, rating = null) {
    try {
      const response = await apiClient.post(COMMENTS_URL, {
        vacancy_id: vacancyId,
        content,
        rating,
      });
      return response.data;
    } catch (err) {
      console.error('Create comment error:', err);
      throw err;
    }
  },

  async updateComment(commentId, data) {
    try {
      const response = await apiClient.patch(`${COMMENTS_URL}${commentId}/`, data);
      return response.data;
    } catch (err) {
      console.error('Update comment error:', err);
      throw err;
    }
  },

  async deleteComment(commentId) {
    try {
      const response = await apiClient.delete(`${COMMENTS_URL}${commentId}/`);
      return response.data;
    } catch (err) {
      console.error('Delete comment error:', err);
      throw err;
    }
  },
};

export default CommentService;
