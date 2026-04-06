import apiClient from '../client';
import { BOOKMARKS_URL } from '../../constants/ApiUrls';

const BookmarkService = {
  async getMyBookmarks() {
    try {
      const response = await apiClient.get(BOOKMARKS_URL);
      return response.data;
    } catch (err) {
      console.error('Get bookmarks error:', err);
      throw err;
    }
  },

  async getMyBookmarkIds() {
    try {
      const response = await apiClient.get(`${BOOKMARKS_URL}ids/`);
      return response.data;
    } catch (err) {
      console.error('Get bookmark ids error:', err);
      throw err;
    }
  },

  async checkBookmark(vacancyId) {
    try {
      const response = await apiClient.get(`${BOOKMARKS_URL}check/${vacancyId}/`);
      return response.data.bookmarked;
    } catch (err) {
      console.error('Check bookmark error:', err);
      throw err;
    }
  },

  async addBookmark(vacancyId) {
    try {
      const response = await apiClient.post(BOOKMARKS_URL, { vacancy_id: vacancyId });
      return response.data;
    } catch (err) {
      console.error('Add bookmark error:', err);
      throw err;
    }
  },

  async toggleBookmark(vacancyId) {
    try {
      const response = await apiClient.post(`${BOOKMARKS_URL}toggle/${vacancyId}/`);
      return response.data;
    } catch (err) {
      console.error('Toggle bookmark error:', err);
      throw err;
    }
  },

  async removeBookmark(vacancyId) {
    try {
      const response = await apiClient.delete(`${BOOKMARKS_URL}${vacancyId}/`);
      return response.data;
    } catch (err) {
      console.error('Remove bookmark error:', err);
      throw err;
    }
  },
};

export default BookmarkService;
