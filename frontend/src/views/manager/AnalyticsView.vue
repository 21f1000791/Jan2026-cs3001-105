<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import AppNavbar from "../../components/ui/AppNavbar.vue";
import AppSidebar from "../../components/ui/AppSidebar.vue";
import LineAnalyticsChart from "../../components/charts/LineAnalyticsChart.vue";
import { authService } from "../../services/authService";
import { dashboardService } from "../../services/dashboardService";
import { notificationService } from "../../services/notificationService";

const router = useRouter();
const darkMode = ref(localStorage.getItem("ui_theme") === "dark");
const notificationOpen = ref(false);
const notifications = ref([]);

const sidebarItems = [
  { key: "tasks", label: "Task Management", route: "/manager/dashboard" },
  { key: "users", label: "User Management", route: "/manager/dashboard" },
  { key: "analytics", label: "Analytics" },
];

const metrics = ref({ total: 0, completed: 0, pending: 0, overdue: 0 });
const chartPoints = ref([]);

const loadNotifications = async () => {
  notifications.value = await notificationService.getUnread();
};

const markNotificationRead = async (notificationId) => {
  await notificationService.markAsRead(notificationId);
  notifications.value = notifications.value.map((notification) =>
    notification.notification_id === notificationId
      ? { ...notification, is_read: true }
      : notification
  );
};

const toggleTheme = () => {
  darkMode.value = !darkMode.value;
  document.documentElement.classList.toggle("dark", darkMode.value);
  localStorage.setItem("ui_theme", darkMode.value ? "dark" : "light");
};

const logout = async () => {
  await authService.logout();
  router.push("/login");
};

onMounted(async () => {
  document.documentElement.classList.toggle("dark", darkMode.value);
  try {
    const [dashboard] = await Promise.all([
      dashboardService.getManagerDashboard(),
      loadNotifications(),
    ]);
    metrics.value = dashboard.metrics;
    chartPoints.value = dashboard.chartPoints;
  } catch (error) {
    metrics.value = { total: 0, completed: 0, pending: 0, overdue: 0 };
    chartPoints.value = [];
  }
});
</script>

<template>
  <div class="analytics-page">
    <div class="analytics-shell">
      <AppNavbar
        title="Analytics"
        subtitle="Performance and task trends"
        :notifications="notifications"
        :notification-open="notificationOpen"
        :dark-mode="darkMode"
        @toggle-theme="toggleTheme"
        @toggle-notifications="notificationOpen = !notificationOpen"
        @mark-notification-read="markNotificationRead"
        @logout="logout"
      />

      <div class="analytics-layout">
        <AppSidebar :items="sidebarItems" model-value="analytics" @navigate="router.push($event)" />

        <section class="analytics-main">
          <div class="analytics-stats-grid">
            <div class="analytics-stat-card glass-panel" v-for="item in [
              { key: 'total', label: 'Total Tasks', value: metrics.total },
              { key: 'completed', label: 'Completed', value: metrics.completed },
              { key: 'pending', label: 'Pending', value: metrics.pending },
              { key: 'overdue', label: 'Overdue', value: metrics.overdue },
            ]" :key="item.key">
              <p class="analytics-stat-label soft-text">{{ item.label }}</p>
              <p class="analytics-stat-value">{{ item.value }}</p>
            </div>
          </div>

          <div class="analytics-chart-card glass-panel">
            <h2 class="analytics-chart-title">Task Flow (Chart.js)</h2>
            <LineAnalyticsChart :points="chartPoints" label="Tasks" />
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.analytics-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f12711 0%, #f5af19 100%);
  padding: 1rem;
}

.analytics-shell {
  max-width: 80rem;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.analytics-layout {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.analytics-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.analytics-stats-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 1rem;
}

.analytics-stat-card {
  border-radius: 1rem;
  padding: 1rem;
}

.analytics-stat-label {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.analytics-stat-value {
  margin: 0.25rem 0 0;
  font-size: 1.875rem;
  line-height: 2.25rem;
  font-weight: 700;
  color: #0f172a;
}

.analytics-chart-card {
  border-radius: 1rem;
  padding: 1rem;
}

.analytics-chart-title {
  margin: 0 0 0.75rem;
  font-size: 1.125rem;
  line-height: 1.75rem;
  font-weight: 600;
  color: #0f172a;
}

:global(html.dark) .analytics-stat-value,
:global(html.dark) .analytics-chart-title {
  color: #f1f5f9;
}

@media (min-width: 640px) {
  .analytics-stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 768px) {
  .analytics-page {
    padding: 1.5rem;
  }

  .analytics-layout {
    flex-direction: row;
  }
}

@media (min-width: 1024px) {
  .analytics-stats-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
</style>
