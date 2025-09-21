import axios from "axios";

const API_URL = "http://localhost:5000/api";

export default {
  async getData() {
    try {
      const response = await axios.get(`${API_URL}/data`);
      return response.data;
    } catch (error) {
      console.error("Ошибка при получении данных:", error);
      throw error;
    }
  },

  async getStats() {
    try {
      const response = await axios.get(`${API_URL}/stats`);
      return response.data;
    } catch (error) {
      console.error("Ошибка при получении статистики:", error);
      throw error;
    }
  },

  async getFeatures() {
    try {
      const response = await axios.get(`${API_URL}/features`);
      return response.data;
    } catch (error) {
      console.error("Ошибка при получении информации о признаках:", error);
      throw error;
    }
  },
};
