import { apiClient } from "./apiClient";

const normalizeUser = (item = {}) => ({
  id: item.id,
  name: item.name || item.full_name || "Unknown",
  email: item.email || "",
  role: (item.role || "staff").toLowerCase(),
  active: item.is_active ?? item.active ?? true,
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
