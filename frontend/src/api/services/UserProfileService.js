import apiClient from '../client';
import { USER_PROFILES_URL } from '../../constants/ApiUrls';

const UserProfileService = {
  async getUserProfile(userId) {
    try {
      const response = await apiClient.get(`${USER_PROFILES_URL}${userId}/`);
      return response.data;
    } catch (err) {
      console.error('Get user profile error:', err);
      throw err;
    }
  },

  async updateUserProfile(userId, data) {
    try {
      const response = await apiClient.patch(`${USER_PROFILES_URL}${userId}/`, data);
      return response.data;
    } catch (err) {
      console.error('Update user profile error:', err);
      throw err;
    }
  },

  async getProfileOptions() {
    try {
      const response = await apiClient.get(`${USER_PROFILES_URL}options/`);
      return response.data;
    } catch (err) {
      console.error('Get profile options error:', err);
      throw err;
    }
  },
};

export default UserProfileService;
