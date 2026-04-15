import { apiClient } from "./apiClient";

const normalizeAuthPayload = (data = {}) => ({
  token: data.token || data.access_token || data.jwt || "",
  role: (data.role || data.user?.role || "staff").toLowerCase(),
  user: data.user || null,
});

export const authService = {
  async login(payload) {
    const response = await apiClient.post("/auth/login", payload);
    const auth = normalizeAuthPayload(response.data);
    if (!auth.token) {
      throw new Error("Login succeeded but token is missing in response");
    }
    return auth;
  },

  async register(payload) {
    const response = await apiClient.post("/auth/register", payload);
    return response.data;
  },

  async logout() {
    try {
      await apiClient.post("/auth/logout");
    } catch (error) {
      // Ignore auth failures during logout because local session teardown should still proceed.
      if (![401, 422].includes(error?.status)) {
        throw error;
      }
    } finally {
      localStorage.removeItem("auth_token");
      localStorage.removeItem("user_role");
    }
  },
};
