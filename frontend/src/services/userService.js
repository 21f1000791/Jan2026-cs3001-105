import { apiClient } from "./apiClient";

const normalizeUser = (item = {}) => ({
  id: item.id,
  name: item.name || item.full_name || "Unknown",
  email: item.email || "",
  role: (item.role || "staff").toLowerCase(),
  active: item.is_active ?? item.active ?? true,
  categories: item.categories || [],
});

export const userService = {
  async getMe() {
    const response = await apiClient.get("/users/me");
    return normalizeUser(response.data?.user || response.data || {});
  },

  async getAll() {
    const response = await apiClient.get("/users");
    const users = response.data?.items || response.data || [];
    return users.map(normalizeUser);
  },

  async getCategoryCatalog() {
    const response = await apiClient.get("/users/categories");
    return {
      allCategories: response.data?.all_categories || [],
      allowedCategories: response.data?.allowed_categories || [],
    };
  },

  async getManagerCategoryMatrix() {
    const response = await apiClient.get("/users/manager-categories");
    return {
      categories: response.data?.categories || [],
      managers: (response.data?.items || []).map(normalizeUser),
    };
  },

  async setManagerCategories(userId, categories) {
    const response = await apiClient.put(`/users/${userId}/categories`, { categories });
    return normalizeUser(response.data?.manager || response.data || { id: userId, categories });
  },

  async create(payload) {
    const response = await apiClient.post("/users", payload);
    return normalizeUser(response.data?.user || response.data || payload);
  },

  async update(userId, payload) {
    const response = await apiClient.put(`/users/${userId}`, payload);
    return normalizeUser(response.data?.user || response.data || { id: userId, ...payload });
  },

  async deactivate(userId) {
    try {
      await apiClient.put(`/users/${userId}/terminate`);
      return;
    } catch (error) {
      await apiClient.patch(`/users/${userId}`, { is_active: false });
    }
  },

  async activate(userId) {
    try {
      await apiClient.put(`/users/${userId}/activate`);
      return;
    } catch (error) {
      await apiClient.patch(`/users/${userId}`, { is_active: true });
    }
  },

  async removeHard(userId) {
    await apiClient.delete(`/users/${userId}/hard`);
  },
};
