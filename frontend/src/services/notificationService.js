import { apiClient } from "./apiClient";

const normalizeNotification = (item = {}) => ({
  notification_id: item.notification_id || item.id,
  type: item.type || "System",
  message: item.message || "",
  is_read: item.is_read ?? false,
  created_at: item.created_at || item.timestamp || "",
});

export const notificationService = {
  async getUnread() {
    const response = await apiClient.get("/notifications");
    const notifications = response.data?.items || response.data || [];
    return notifications.map(normalizeNotification);
  },

  async markAsRead(notificationId) {
    await apiClient.patch(`/notifications/${notificationId}/read`, {
      is_read: true,
    });
  },
};
