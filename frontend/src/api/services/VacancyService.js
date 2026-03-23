import apiClient from '../client';

const VacancyService = {
  /**
   * Получить список вакансий с пагинацией
   * @param {Object} params - Параметры запроса
   * @param {number} params.page - Номер страницы (по умолчанию 1)
   * @param {number} params.page_size - Количество элементов на странице (по умолчанию 10)
   * @returns {Promise<{items: Array, pagination: Object}>}
   */
  async getVacancies(params = {}) {
    const { page = 1, page_size = 10 } = params;
    const response = await apiClient.get('/vacancies/', {
      params: { page, page_size },
    });
    return response.data;
  },

  /**
   * Получить вакансию по ID
   * @param {number} id - ID вакансии
   * @returns {Promise<Object>}
   */
  async getVacancyById(id) {
    const response = await apiClient.get(`/vacancies/${id}/`);
    return response.data;
  },

  /**
   * Создать новую вакансию
   * @param {Object} data - Данные вакансии
   * @returns {Promise<Object>}
   */
  async createVacancy(data) {
    const response = await apiClient.post('/vacancies/', data);
    return response.data;
  },

  /**
   * Обновить вакансию
   * @param {number} id - ID вакансии
   * @param {Object} data - Данные для обновления
   * @returns {Promise<Object>}
   */
  async updateVacancy(id, data) {
    const response = await apiClient.patch(`/vacancies/${id}/`, data);
    return response.data;
  },

  /**
   * Удалить вакансию
   * @param {number} id - ID вакансии
   * @returns {Promise<Object>}
   */
  async deleteVacancy(id) {
    const response = await apiClient.delete(`/vacancies/${id}/`);
    return response.data;
  },
};

export default VacancyService;
