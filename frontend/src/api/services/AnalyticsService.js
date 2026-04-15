import apiClient from '../client';

const ANALYTICS_URL = '/analytics/';

const AnalyticsService = {
  // Полный дашборд
  async getFullDashboard(days = 30) {
    try {
      const response = await apiClient.get(`${ANALYTICS_URL}dashboard/`, {
        params: { days },
      });
      return response.data;
    } catch (err) {
      console.error('Get full dashboard error:', err);
      throw err;
    }
  },

  // Краткая сводка
  async getDashboardSummary() {
    try {
      const response = await apiClient.get(`${ANALYTICS_URL}dashboard/summary/`);
      return response.data;
    } catch (err) {
      console.error('Get dashboard summary error:', err);
      throw err;
    }
  },

  // Общая статистика
  async getOverviewStats() {
    try {
      const response = await apiClient.get(`${ANALYTICS_URL}overview/`);
      return response.data;
    } catch (err) {
      console.error('Get overview stats error:', err);
      throw err;
    }
  },

  // Статистика с трендами
  async getOverviewWithTrends(days = 30) {
    try {
      const response = await apiClient.get(`${ANALYTICS_URL}overview/trends/`, {
        params: { days },
      });
      return response.data;
    } catch (err) {
      console.error('Get overview with trends error:', err);
      throw err;
    }
  },

  // Временной ряд вакансий
  async getVacanciesTimeSeries(period = 'day', days = 30) {
    try {
      const response = await apiClient.get(`${ANALYTICS_URL}vacancies/time-series/`, {
        params: { period, days },
      });
      return response.data;
    } catch (err) {
      console.error('Get vacancies time series error:', err);
      throw err;
    }
  },

  // Статистика по зарплатам
  async getSalaryStats(currencyId = null) {
    try {
      const params = currencyId ? { currency_id: currencyId } : {};
      const response = await apiClient.get(`${ANALYTICS_URL}salary/`, { params });
      return response.data;
    } catch (err) {
      console.error('Get salary stats error:', err);
      throw err;
    }
  },

  // Топ компаний
  async getTopCompanies(limit = 10) {
    try {
      const response = await apiClient.get(`${ANALYTICS_URL}top/companies/`, {
        params: { limit },
      });
      return response.data;
    } catch (err) {
      console.error('Get top companies error:', err);
      throw err;
    }
  },

  // Топ навыков
  async getTopSkills(limit = 20) {
    try {
      const response = await apiClient.get(`${ANALYTICS_URL}top/skills/`, {
        params: { limit },
      });
      return response.data;
    } catch (err) {
      console.error('Get top skills error:', err);
      throw err;
    }
  },

  // Топ городов
  async getTopCities(limit = 10) {
    try {
      const response = await apiClient.get(`${ANALYTICS_URL}top/cities/`, {
        params: { limit },
      });
      return response.data;
    } catch (err) {
      console.error('Get top cities error:', err);
      throw err;
    }
  },

  // Статистика по источникам
  async getSourcesStats() {
    try {
      const response = await apiClient.get(`${ANALYTICS_URL}sources/`);
      return response.data;
    } catch (err) {
      console.error('Get sources stats error:', err);
      throw err;
    }
  },

  // Статистика парсинга
  async getSourceParsingStats(days = 7) {
    try {
      const response = await apiClient.get(`${ANALYTICS_URL}sources/parsing/`, {
        params: { days },
      });
      return response.data;
    } catch (err) {
      console.error('Get source parsing stats error:', err);
      throw err;
    }
  },

  // Активность пользователей
  async getUserActivityStats() {
    try {
      const response = await apiClient.get(`${ANALYTICS_URL}users/activity/`);
      return response.data;
    } catch (err) {
      console.error('Get user activity stats error:', err);
      throw err;
    }
  },

  // Пользователи по ролям
  async getUsersByRole() {
    try {
      const response = await apiClient.get(`${ANALYTICS_URL}users/by-role/`);
      return response.data;
    } catch (err) {
      console.error('Get users by role error:', err);
      throw err;
    }
  },

  // Регистрации пользователей
  async getUserRegistrations(days = 30) {
    try {
      const response = await apiClient.get(`${ANALYTICS_URL}users/registrations/`, {
        params: { days },
      });
      return response.data;
    } catch (err) {
      console.error('Get user registrations error:', err);
      throw err;
    }
  },

  // Детальная статистика по вакансиям
  async getVacancyDetailedStats() {
    try {
      const response = await apiClient.get(`${ANALYTICS_URL}vacancies/detailed/`);
      return response.data;
    } catch (err) {
      console.error('Get vacancy detailed stats error:', err);
      throw err;
    }
  },
};

export default AnalyticsService;
