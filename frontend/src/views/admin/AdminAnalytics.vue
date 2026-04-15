<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { Bar, Doughnut, Line } from "vue-chartjs";
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
} from "chart.js";
import AppNavbar from "../../components/ui/AppNavbar.vue";
import AppSidebar from "../../components/ui/AppSidebar.vue";
import ToastStack from "../../components/ui/ToastStack.vue";
import { authService } from "../../services/authService";
import { dashboardService } from "../../services/dashboardService";
import { notificationService } from "../../services/notificationService";

ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Title,
  Tooltip
);

const router = useRouter();
const darkMode = ref(localStorage.getItem("ui_theme") === "dark");
const notificationOpen = ref(false);
const notifications = ref([]);
const loading = ref(true);

const metrics = ref({ total: 0, completed: 0, pending: 0, overdue: 0 });
const analytics = ref({
  monthlyCreated: [],
  monthlyCompleted: [],
  statusBreakdown: [],
  priorityBreakdown: [],
  categoryBreakdown: [],
  staffPerformance: [],
  usersByRole: { admin: 0, manager: 0, staff: 0 },
  notifications: { total: 0, unread: 0 },
  translationCoverage: { multilingualTasks: 0, expectedRows: 0, actualRows: 0, coveragePct: 0 },
  overdueRate: 0,
  dueSoonTasks: 0,
});

const toasts = ref([]);
const pushToast = (message, type = "info") => {
  const id = Date.now() + Math.floor(Math.random() * 1000);
  toasts.value.push({ id, message, type });
  setTimeout(() => {
    toasts.value = toasts.value.filter((toast) => toast.id !== id);
  }, 2600);
};

const sidebarItems = [
  { key: "dashboard", label: "Admin Analytics" },
  { key: "manager", label: "Manager Workspace", route: "/manager/dashboard" },
  { key: "staff", label: "Staff Workspace", route: "/staff/tasks" },
];

const kpiCards = computed(() => [
  { key: "total", label: "Total Tasks", value: metrics.value.total },
  { key: "completed", label: "Completed", value: metrics.value.completed },
  { key: "pending", label: "Pending", value: metrics.value.pending },
  { key: "overdue", label: "Overdue", value: metrics.value.overdue },
  { key: "dueSoon", label: "Due In 3 Days", value: analytics.value.dueSoonTasks },
  { key: "overdueRate", label: "Overdue %", value: `${analytics.value.overdueRate.toFixed(1)}%` },
  {
    key: "coverage",
    label: "Translation Coverage",
    value: `${analytics.value.translationCoverage.coveragePct.toFixed(1)}%`,
  },
  { key: "unread", label: "Unread Notifications", value: analytics.value.notifications.unread },
]);

const trendChartData = computed(() => {
  const labels = analytics.value.monthlyCreated.map((point) => point.label);
  return {
    labels,
    datasets: [
      {
        label: "Created",
        data: analytics.value.monthlyCreated.map((point) => point.value),
        borderColor: "#0ea5e9",
        backgroundColor: "rgba(14, 165, 233, 0.2)",
        tension: 0.35,
        fill: true,
        pointRadius: 3,
      },
      {
        label: "Completed",
        data: analytics.value.monthlyCompleted.map((point) => point.value),
        borderColor: "#10b981",
        backgroundColor: "rgba(16, 185, 129, 0.18)",
        tension: 0.35,
        fill: true,
        pointRadius: 3,
      },
    ],
  };
});

const statusChartData = computed(() => ({
  labels: analytics.value.statusBreakdown.map((item) => item.label),
  datasets: [
    {
      label: "Tasks",
      data: analytics.value.statusBreakdown.map((item) => item.value),
      backgroundColor: ["#10b981", "#0ea5e9", "#6366f1", "#f59e0b", "#ef4444"],
    },
  ],
}));

const priorityChartData = computed(() => ({
  labels: analytics.value.priorityBreakdown.map((item) => item.label),
  datasets: [
    {
      label: "Tasks",
      data: analytics.value.priorityBreakdown.map((item) => item.value),
      backgroundColor: ["#22c55e", "#3b82f6", "#f97316", "#ef4444"],
      borderRadius: 6,
      borderSkipped: false,
    },
  ],
}));

const userRoleChartData = computed(() => ({
  labels: ["Admin", "Manager", "Staff"],
  datasets: [
    {
      label: "Active Users",
      data: [
        analytics.value.usersByRole.admin,
        analytics.value.usersByRole.manager,
        analytics.value.usersByRole.staff,
      ],
      backgroundColor: ["#7c3aed", "#0284c7", "#16a34a"],
    },
  ],
}));

const topStaff = computed(() => {
  const rows = [...(analytics.value.staffPerformance || [])];
  rows.sort((a, b) => Number(b.completion_rate || 0) - Number(a.completion_rate || 0));
  return rows.slice(0, 6);
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: "top",
    },
  },
};

const loadNotifications = async () => {
  try {
    notifications.value = await notificationService.getUnread();
  } catch (error) {
    pushToast("Could not load notifications.", "error");
  }
};

const markNotificationRead = async (notificationId) => {
  try {
    await notificationService.markAsRead(notificationId);
    notifications.value = notifications.value.map((notification) =>
      notification.notification_id === notificationId
        ? { ...notification, is_read: true }
        : notification
    );
  } catch (error) {
    pushToast("Could not mark notification as read.", "error");
  }
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
  loading.value = true;
  try {
    const [dashboard] = await Promise.all([
      dashboardService.getManagerDashboard(),
      loadNotifications(),
    ]);
    metrics.value = dashboard.metrics;
    analytics.value = dashboard.analytics;
  } catch (error) {
    pushToast("Could not load analytics.", "error");
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="admin-page">
    <div class="admin-shell">
      <AppNavbar
        title="Admin Analytics"
        subtitle="Operations intelligence across tasks, users, and translations"
        :notifications="notifications"
        :notification-open="notificationOpen"
        :dark-mode="darkMode"
        @toggle-theme="toggleTheme"
        @toggle-notifications="notificationOpen = !notificationOpen"
        @mark-notification-read="markNotificationRead"
        @logout="logout"
      />

      <div class="admin-layout">
        <AppSidebar :items="sidebarItems" model-value="dashboard" @navigate="router.push($event)" />

        <section class="admin-main">
          <div class="admin-kpi-grid">
            <div v-for="item in kpiCards" :key="item.key" class="admin-kpi glass-panel">
              <p class="admin-kpi__label soft-text">{{ item.label }}</p>
              <p class="admin-kpi__value">{{ item.value }}</p>
            </div>
          </div>

          <div class="admin-chart-grid">
            <div class="admin-chart-card glass-panel admin-chart-card--wide">
              <h2 class="admin-chart__title">6-Month Throughput</h2>
              <div class="admin-chart__canvas">
                <Line :data="trendChartData" :options="chartOptions" />
              </div>
            </div>

            <div class="admin-chart-card glass-panel">
              <h2 class="admin-chart__title">Task Status Mix</h2>
              <div class="admin-chart__canvas">
                <Doughnut :data="statusChartData" :options="chartOptions" />
              </div>
            </div>

            <div class="admin-chart-card glass-panel">
              <h2 class="admin-chart__title">Priority Pressure</h2>
              <div class="admin-chart__canvas">
                <Bar :data="priorityChartData" :options="chartOptions" />
              </div>
            </div>

            <div class="admin-chart-card glass-panel">
              <h2 class="admin-chart__title">Active User Roles</h2>
              <div class="admin-chart__canvas">
                <Doughnut :data="userRoleChartData" :options="chartOptions" />
              </div>
            </div>

            <div class="admin-chart-card glass-panel">
              <h2 class="admin-chart__title">Top Categories</h2>
              <ul class="admin-list">
                <li v-for="item in analytics.categoryBreakdown.slice(0, 6)" :key="item.label" class="admin-list__item">
                  <span>{{ item.label }}</span>
                  <strong>{{ item.value }}</strong>
                </li>
              </ul>
            </div>

            <div class="admin-chart-card glass-panel">
              <h2 class="admin-chart__title">Top Staff Completion</h2>
              <ul class="admin-list">
                <li v-for="row in topStaff" :key="row.staff_id" class="admin-list__item">
                  <span>{{ row.staff_name || `Staff ${row.staff_id}` }}</span>
                  <strong>{{ Number(row.completion_rate || 0).toFixed(1) }}%</strong>
                </li>
                <li v-if="!topStaff.length" class="admin-list__item">
                  <span>No staff performance data yet</span>
                </li>
              </ul>
            </div>
          </div>

          <div v-if="loading" class="admin-loading glass-panel">Loading analytics...</div>
        </section>
      </div>
    </div>

    <ToastStack :items="toasts" />
  </div>
</template>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: radial-gradient(circle at 10% 10%, #eef2ff 0%, #ecfeff 45%, #f0fdf4 100%);
  padding: 1rem;
}

.admin-shell {
  max-width: 84rem;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.admin-layout {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.admin-main {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  flex: 1;
}

.admin-kpi-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.admin-kpi {
  border-radius: 1rem;
  padding: 0.9rem;
}

.admin-kpi__label {
  margin: 0;
  font-size: 0.8rem;
}

.admin-kpi__value {
  margin: 0.3rem 0 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
}

.admin-chart-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 1rem;
}

.admin-chart-card {
  border-radius: 1rem;
  padding: 1rem;
}

.admin-chart-card--wide {
  grid-column: span 1;
}

.admin-chart__title {
  margin: 0 0 0.75rem;
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
}

.admin-chart__canvas {
  height: 18rem;
}

.admin-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.admin-list__item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.7rem;
  border-radius: 0.65rem;
  background: rgba(255, 255, 255, 0.65);
  color: #1e293b;
}

.admin-loading {
  border-radius: 1rem;
  padding: 0.9rem;
  color: #334155;
}

:global(html.dark) .admin-page {
  background: radial-gradient(circle at 15% 20%, #0f172a 0%, #111827 60%, #052e16 100%);
}

:global(html.dark) .admin-kpi__value,
:global(html.dark) .admin-chart__title {
  color: #f8fafc;
}

:global(html.dark) .admin-list__item {
  background: rgba(30, 41, 59, 0.72);
  color: #e2e8f0;
}

:global(html.dark) .admin-loading {
  color: #cbd5e1;
}

@media (min-width: 768px) {
  .admin-page {
    padding: 1.5rem;
  }

  .admin-layout {
    flex-direction: row;
  }

  .admin-kpi-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .admin-chart-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .admin-chart-card--wide {
    grid-column: span 2;
  }
}
</style>
