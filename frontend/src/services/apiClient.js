import axios from "axios";

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || "http://127.0.0.1:5000/api";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
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
    const lowerMessage = String(message).toLowerCase();
    const isAuthTokenIssue =
      status === 401 ||
      (status === 422 &&
        (lowerMessage.includes("token") ||
          lowerMessage.includes("jwt") ||
          lowerMessage.includes("signature") ||
          lowerMessage.includes("subject") ||
          lowerMessage.includes("not enough segments")));

    if (isAuthTokenIssue) {
      localStorage.removeItem("auth_token");
      localStorage.removeItem("user_role");
      window.dispatchEvent(new CustomEvent("cop:auth-expired"));
    }

    const wrappedError = new Error(message);
    wrappedError.status = status;
    return Promise.reject(wrappedError);
  }
);
