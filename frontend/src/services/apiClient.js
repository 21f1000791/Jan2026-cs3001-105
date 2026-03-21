import axios from "axios";

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || "http://127.0.0.1:5000/api";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    const message =
      error?.response?.data?.message ||
      error?.response?.data?.error ||
      error?.message ||
      "Request failed";

    if (status === 401) {
      localStorage.removeItem("auth_token");
      localStorage.removeItem("user_role");
      window.dispatchEvent(new CustomEvent("cop:auth-expired"));
    }

    return Promise.reject(new Error(message));
  }
);
