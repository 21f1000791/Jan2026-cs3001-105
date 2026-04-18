<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { Doughnut } from "vue-chartjs";
import { ArcElement, Chart as ChartJS, Legend, Tooltip } from "chart.js";
import AppNavbar from "../../components/ui/AppNavbar.vue";
import AppSidebar from "../../components/ui/AppSidebar.vue";
import TaskCard from "../../components/tasks/TaskCard.vue";
import TaskModal from "../../components/tasks/TaskModal.vue";
import UserModal from "../../components/ui/UserModal.vue";
import LineAnalyticsChart from "../../components/charts/LineAnalyticsChart.vue";
import SkeletonCard from "../../components/ui/SkeletonCard.vue";
import ToastStack from "../../components/ui/ToastStack.vue";
import { authService } from "../../services/authService";
import { dashboardService } from "../../services/dashboardService";
import { taskService } from "../../services/taskService";
import { userService } from "../../services/userService";
import { notificationService } from "../../services/notificationService";
import ChatBot from "../../components/ui/ChatBot.vue";

ChartJS.register(ArcElement, Legend, Tooltip);

const router = useRouter();

const currentUser = ref({ name: "", role: "manager", categories: [] });
const notifications = ref([]);
const notificationOpen = ref(false);
const darkMode = ref(localStorage.getItem("ui_theme") === "dark");

const sidebarItems = computed(() => [
  { key: "tasks", label: "Task Management" },
  { key: "users", label: "User Management" },
  { key: "analytics", label: "Analytics" },
]);
const activePanel = ref("tasks");

const loadingTasks = ref(true);
const loadingUsers = ref(true);
const savingTask = ref(false);
const analyticsLoading = ref(false);
const tasks = ref([]);
const taskSearch = ref("");
const showTaskModal = ref(false);
const editingTask = ref(null);

const analyticsMetrics = ref({ total: 0, completed: 0, pending: 0, overdue: 0 });
const analyticsData = ref({
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

const users = ref([]);
const userSearch = ref("");
const showUserModal = ref(false);
const editingUser = ref(null);
const categoryCatalog = ref({ allCategories: [], allowedCategories: [] });
const managerCategoryState = ref({ categories: [], managers: [] });
const loadingManagerCategories = ref(false);

const toasts = ref([]);
const pushToast = (message, type = "info") => {
  const id = Date.now() + Math.floor(Math.random() * 1000);
  toasts.value.push({ id, message, type });
  setTimeout(() => {
    toasts.value = toasts.value.filter((toast) => toast.id !== id);
  }, 2800);
};

const staffUsers = computed(() =>
  users.value.filter((user) => user.role === "staff" && user.active)
);

const isAdmin = computed(() => currentUser.value.role === "admin");

const taskCategoryOptions = computed(() => {
  if (isAdmin.value) {
    return categoryCatalog.value.allCategories;
  }
  return categoryCatalog.value.allowedCategories;
});

const filteredTasks = computed(() => {
  const query = taskSearch.value.trim().toLowerCase();
  if (!query) {
    return tasks.value;
  }

  return tasks.value.filter((task) => {
    return (
      task.title.toLowerCase().includes(query) ||
      task.category.toLowerCase().includes(query) ||
      String(task.assignedTo || "").toLowerCase().includes(query)
    );
  });
});

const filteredUsers = computed(() => {
  const query = userSearch.value.trim().toLowerCase();
  if (!query) {
    return users.value;
  }

  return users.value.filter((user) => {
    return (
      user.name.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query) ||
      user.role.toLowerCase().includes(query)
    );
  });
});

const analyticsKpis = computed(() => [
  { key: "total", label: "Total Tasks", value: analyticsMetrics.value.total },
  { key: "completed", label: "Completed", value: analyticsMetrics.value.completed },
  { key: "pending", label: "Pending", value: analyticsMetrics.value.pending },
  { key: "overdue", label: "Overdue", value: analyticsMetrics.value.overdue },
  { key: "dueSoon", label: "Due In 3 Days", value: analyticsData.value.dueSoonTasks },
  { key: "overdueRate", label: "Overdue %", value: `${Number(analyticsData.value.overdueRate || 0).toFixed(1)}%` },
  {
    key: "coverage",
    label: "Translation Coverage",
    value: `${Number(analyticsData.value.translationCoverage?.coveragePct || 0).toFixed(1)}%`,
  },
  { key: "unread", label: "Unread Notifications", value: analyticsData.value.notifications?.unread || 0 },
]);

const createdTrendPoints = computed(() => analyticsData.value.monthlyCreated || []);

const topCategories = computed(() => (analyticsData.value.categoryBreakdown || []).slice(0, 6));

const topStaff = computed(() => {
  const rows = [...(analyticsData.value.staffPerformance || [])];
  rows.sort((a, b) => Number(b.completion_rate || 0) - Number(a.completion_rate || 0));
  return rows.slice(0, 6);
});

const usersByRoleRows = computed(() => [
  { label: "Admin", value: analyticsData.value.usersByRole?.admin || 0 },
  { label: "Manager", value: analyticsData.value.usersByRole?.manager || 0 },
  { label: "Staff", value: analyticsData.value.usersByRole?.staff || 0 },
]);

const statusChartData = computed(() => ({
  labels: (analyticsData.value.statusBreakdown || []).map((item) => item.label),
  datasets: [
    {
      data: (analyticsData.value.statusBreakdown || []).map((item) => item.value),
      backgroundColor: ["#10b981", "#0ea5e9", "#6366f1", "#f59e0b", "#ef4444"],
      borderWidth: 0,
    },
  ],
}));

const usersByRoleChartData = computed(() => ({
  labels: usersByRoleRows.value.map((row) => row.label),
  datasets: [
    {
      data: usersByRoleRows.value.map((row) => row.value),
      backgroundColor: ["#7c3aed", "#0284c7", "#16a34a"],
      borderWidth: 0,
    },
  ],
}));

const donutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: "bottom",
      labels: {
        boxWidth: 12,
      },
    },
  },
};

const loadTasks = async () => {
  loadingTasks.value = true;
  try {
    tasks.value = await taskService.getAll();
  } catch (error) {
    pushToast(error.message || "Could not load tasks.", "error");
  } finally {
    loadingTasks.value = false;
  }
};

const loadCurrentUser = async () => {
  try {
    currentUser.value = await userService.getMe();
  } catch (error) {
    pushToast(error.message || "Could not load profile.", "error");
  }
};

const loadCategoryCatalog = async () => {
  try {
    categoryCatalog.value = await taskService.getCategoryCatalog();
  } catch (error) {
    pushToast(error.message || "Could not load categories.", "error");
  }
};

const loadManagerCategoryMatrix = async () => {
  if (!isAdmin.value) {
    return;
  }

  loadingManagerCategories.value = true;
  try {
    managerCategoryState.value = await userService.getManagerCategoryMatrix();
  } catch (error) {
    pushToast(error.message || "Could not load manager jurisdictions.", "error");
  } finally {
    loadingManagerCategories.value = false;
  }
};

const loadUsers = async () => {
  loadingUsers.value = true;
  try {
    users.value = await userService.getAll();
  } catch (error) {
    pushToast(error.message || "Could not load users.", "error");
  } finally {
    loadingUsers.value = false;
  }
};

const loadNotifications = async () => {
  try {
    notifications.value = await notificationService.getUnread();
  } catch (error) {
    pushToast(error.message || "Could not load notifications.", "error");
  }
};

const loadAnalytics = async () => {
  analyticsLoading.value = true;
  try {
    const dashboard = await dashboardService.getManagerDashboard();
    analyticsMetrics.value = dashboard.metrics;
    analyticsData.value = dashboard.analytics;
  } catch (error) {
    pushToast(error.message || "Could not load analytics.", "error");
  } finally {
    analyticsLoading.value = false;
  }
};

const openCreateTask = () => {
    if (!taskCategoryOptions.value.length) {
      pushToast("No categories are available for your account.", "error");
      return;
    }
    editingTask.value = null;
    showTaskModal.value = true;
};

const openEditTask = (task) => {
  editingTask.value = task;
  showTaskModal.value = true;
};

const saveTask = async (payload) => {
  savingTask.value = true;
  try {
    if (editingTask.value) {
      await taskService.update(editingTask.value.id, payload);
      pushToast("Task updated.", "success");
    } else {
      await taskService.create(payload);
      pushToast("Task created.", "success");
    }

    showTaskModal.value = false;
    editingTask.value = null;
    await loadTasks();
  } catch (error) {
    const message = String(error?.message || "").toLowerCase();
    const isTimeout = message.includes("timeout") || message.includes("aborted");
    pushToast(
      isTimeout
        ? "Task save is still processing translations. Please wait and refresh tasks in a moment."
        : (error.message || "Failed to save task."),
      "error"
    );
  } finally {
    savingTask.value = false;
  }
};

const removeTask = async (taskId) => {
  try {
    await taskService.remove(taskId);
    tasks.value = tasks.value.filter((task) => task.id !== taskId);
    pushToast("Task deleted.", "success");
  } catch (error) {
    pushToast(error.message || "Failed to delete task.", "error");
  }
};

const openCreateUser = () => {
  editingUser.value = null;
  showUserModal.value = true;
};

const openEditUser = (user) => {
  editingUser.value = user;
  showUserModal.value = true;
};

const saveUser = async (payload) => {
  try {
    if (editingUser.value) {
      await userService.update(editingUser.value.id, payload);
      pushToast("User updated.", "success");
    } else {
      await userService.create(payload);
      pushToast("User created.", "success");
    }
    showUserModal.value = false;
    editingUser.value = null;
    await loadUsers();
  } catch (error) {
    pushToast(error.message || "Failed to save user.", "error");
  }
};

const toggleUserStatus = async (user) => {
  try {
    if (user.active) {
      await userService.deactivate(user.id);
      pushToast("User deactivated.", "success");
    } else {
      await userService.activate(user.id);
      pushToast("User activated.", "success");
    }
    await loadUsers();
  } catch (error) {
    pushToast(error.message || "Failed to update user status.", "error");
  }
};

const hardDeleteUser = async (user) => {
  if (!isAdmin.value) {
    pushToast("Only admin can hard delete users.", "error");
    return;
  }

  if (!window.confirm(`Permanently delete ${user.name}? This cannot be undone.`)) {
    return;
  }

  try {
    await userService.removeHard(user.id);
    pushToast("User permanently deleted.", "success");
    await loadUsers();
  } catch (error) {
    pushToast(error.message || "Hard delete endpoint is unavailable.", "error");
  }
};

const toggleManagerCategory = async (manager, category) => {
  const hasCategory = (manager.categories || []).includes(category);
  const nextCategories = hasCategory
    ? (manager.categories || []).filter((item) => item !== category)
    : [...(manager.categories || []), category];

  try {
    await userService.setManagerCategories(manager.id, nextCategories);
    await loadManagerCategoryMatrix();
    pushToast("Manager jurisdiction updated.", "success");
  } catch (error) {
    pushToast(error.message || "Failed to update manager jurisdiction.", "error");
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
    pushToast(error.message || "Could not mark notification as read.", "error");
  }
};

const toggleTheme = () => {
  darkMode.value = !darkMode.value;
  document.documentElement.classList.toggle("dark", darkMode.value);
  localStorage.setItem("ui_theme", darkMode.value ? "dark" : "light");
};

const handleSidebarNavigate = (route) => {
  router.push(route);
};

const logout = async () => {
  await authService.logout();
  router.push("/login");
};

onMounted(async () => {
  document.documentElement.classList.toggle("dark", darkMode.value);
  await loadCurrentUser();
  await Promise.all([loadCategoryCatalog(), loadTasks(), loadUsers(), loadNotifications(), loadAnalytics()]);
  await loadManagerCategoryMatrix();
});
</script>

<template>
  <div class="manager-page">
    <div class="manager-shell">
      <AppNavbar
        :title="isAdmin ? 'Admin Portal' : 'Manager Portal'"
        :subtitle="`Welcome, ${currentUser.name}`"
        :notifications="notifications"
        :notification-open="notificationOpen"
        :dark-mode="darkMode"
        @toggle-theme="toggleTheme"
        @toggle-notifications="notificationOpen = !notificationOpen"
        @mark-notification-read="markNotificationRead"
        @logout="logout"
      />


      <div class="manager-layout">
        <AppSidebar
          v-model="activePanel"
          :items="sidebarItems"
          @navigate="handleSidebarNavigate"
        />

        <section class="manager-main">
          <div v-if="activePanel === 'tasks'" class="manager-panel">
            <div class="manager-toolbar glass-panel">
              <input
                v-model="taskSearch"
                type="text"
                placeholder="Search tasks, staff or category..."
                class="manager-input"
              />
              <button
                @click="openCreateTask"
                class="manager-button manager-button--create-task"
              >
                + Create Task
              </button>
            </div>

            <div class="manager-task-grid">
              <template v-if="loadingTasks">
                <SkeletonCard v-for="idx in 6" :key="idx" />
              </template>

              <TaskCard
                v-for="task in filteredTasks"
                v-else
                :key="task.id"
                :task="task"
                manager-view
                @edit="openEditTask(task)"
                @delete="removeTask(task.id)"
              />
            </div>
          </div>

          <div v-if="activePanel === 'users'" class="manager-panel">
            <div class="manager-toolbar glass-panel">
              <input
                v-model="userSearch"
                type="text"
                placeholder="Search users by name, email, role..."
                class="manager-input"
              />
              <button
                @click="openCreateUser"
                class="manager-button manager-button--add-user"
              >
                + Add User
              </button>
            </div>

            <div class="manager-users-table-wrap glass-panel">
              <h2 class="manager-users-title">User Accounts</h2>
              <table class="manager-users-table">
                <thead>
                  <tr class="manager-users-head-row">
                    <th class="manager-users-cell">Name</th>
                    <th class="manager-users-cell">Email</th>
                    <th class="manager-users-cell">Role</th>
                    <th class="manager-users-cell">Status</th>
                    <th class="manager-users-cell">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="loadingUsers">
                    <td colspan="5" class="manager-users-empty">Loading users...</td>
                  </tr>

                  <tr
                    v-for="user in filteredUsers"
                    v-else
                    :key="user.id"
                    class="manager-users-row"
                  >
                    <td class="manager-users-cell">{{ user.name }}</td>
                    <td class="manager-users-cell">{{ user.email }}</td>
                    <td class="manager-users-cell manager-users-cell--capitalize">{{ user.role }}</td>
                    <td class="manager-users-cell">
                      <span
                        class="manager-status-chip"
                        :class="user.active ? 'manager-status-chip--active' : 'manager-status-chip--inactive'"
                      >
                        {{ user.active ? "Active" : "Inactive" }}
                      </span>
                    </td>
                    <td class="manager-users-cell">
                      <div class="manager-users-actions">
                        <button
                          @click="openEditUser(user)"
                          class="manager-action manager-action--edit"
                        >
                          Edit
                        </button>
                        <button
                          @click="toggleUserStatus(user)"
                          class="manager-action"
                          :class="user.active ? 'manager-action--deactivate' : 'manager-action--activate'"
                        >
                          {{ user.active ? "Deactivate" : "Activate" }}
                        </button>
                        <button
                          v-if="isAdmin"
                          @click="hardDeleteUser(user)"
                          class="manager-action manager-action--delete"
                        >
                          Hard Delete
                        </button>
                      </div>
                    </td>
                  </tr>

                  <tr v-if="!loadingUsers && filteredUsers.length === 0">
                    <td colspan="5" class="manager-users-empty">No users found.</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div v-if="isAdmin" class="manager-users-table-wrap glass-panel">
              <h2 class="manager-users-title">Manager Category Jurisdiction</h2>
              <table class="manager-users-table">
                <thead>
                  <tr class="manager-users-head-row">
                    <th class="manager-users-cell">Manager</th>
                    <th
                      v-for="category in managerCategoryState.categories"
                      :key="category"
                      class="manager-users-cell"
                    >
                      {{ category }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="loadingManagerCategories">
                    <td :colspan="managerCategoryState.categories.length + 1" class="manager-users-empty">
                      Loading manager jurisdictions...
                    </td>
                  </tr>

                  <tr
                    v-for="manager in managerCategoryState.managers"
                    v-else
                    :key="manager.id"
                    class="manager-users-row"
                  >
                    <td class="manager-users-cell">{{ manager.name }}</td>
                    <td
                      v-for="category in managerCategoryState.categories"
                      :key="`${manager.id}-${category}`"
                      class="manager-users-cell"
                    >
                      <label class="manager-category-check-wrap">
                        <input
                          type="checkbox"
                          class="manager-category-check"
                          :checked="(manager.categories || []).includes(category)"
                          @change="toggleManagerCategory(manager, category)"
                        />
                      </label>
                    </td>
                  </tr>

                  <tr v-if="!loadingManagerCategories && managerCategoryState.managers.length === 0">
                    <td :colspan="managerCategoryState.categories.length + 1" class="manager-users-empty">
                      No manager users found.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-if="activePanel === 'analytics'" class="manager-panel">
            <div class="manager-analytics-grid">
              <div v-for="item in analyticsKpis" :key="item.key" class="manager-analytics-kpi glass-panel">
                <p class="manager-analytics-kpi__label soft-text">{{ item.label }}</p>
                <p class="manager-analytics-kpi__value">{{ item.value }}</p>
              </div>
            </div>

            <div class="manager-analytics-cards">
              <div class="manager-analytics-card glass-panel manager-analytics-card--wide">
                <h2 class="manager-analytics-title">6-Month Task Creation Trend</h2>
                <LineAnalyticsChart :points="createdTrendPoints" label="Created Tasks" />
              </div>

              <div class="manager-analytics-card glass-panel">
                <h2 class="manager-analytics-title">Top Categories</h2>
                <ul class="manager-analytics-list">
                  <li v-for="item in topCategories" :key="item.label" class="manager-analytics-list__item">
                    <span>{{ item.label }}</span>
                    <strong>{{ item.value }}</strong>
                  </li>
                  <li v-if="!topCategories.length" class="manager-analytics-list__item">
                    <span>No category data yet</span>
                  </li>
                </ul>
              </div>

              <div class="manager-analytics-card glass-panel">
                <h2 class="manager-analytics-title">Top Staff Completion</h2>
                <ul class="manager-analytics-list">
                  <li v-for="row in topStaff" :key="row.staff_id" class="manager-analytics-list__item">
                    <span>{{ row.staff_name || `Staff ${row.staff_id}` }}</span>
                    <strong>{{ Number(row.completion_rate || 0).toFixed(1) }}%</strong>
                  </li>
                  <li v-if="!topStaff.length" class="manager-analytics-list__item">
                    <span>No staff performance data yet</span>
                  </li>
                </ul>
              </div>

              <div class="manager-analytics-card glass-panel">
                <h2 class="manager-analytics-title">Task Status Mix</h2>
                <div class="manager-analytics-donut">
                  <Doughnut :data="statusChartData" :options="donutOptions" />
                </div>
              </div>

              <div class="manager-analytics-card glass-panel">
                <h2 class="manager-analytics-title">Active Users by Role</h2>
                <div class="manager-analytics-donut">
                  <Doughnut :data="usersByRoleChartData" :options="donutOptions" />
                </div>
              </div>
            </div>

            <div v-if="analyticsLoading" class="manager-analytics-loading glass-panel">
              Loading analytics...
            </div>
          </div>
        </section>
      </div>
    </div>

    <TaskModal
      :open="showTaskModal"
      :editing-task="editingTask"
      :users="staffUsers"
      :categories="taskCategoryOptions"
      :saving="savingTask"
      @close="showTaskModal = false"
      @submit="saveTask"
    />

    <UserModal
      :open="showUserModal"
      :editing-user="editingUser"
      :allow-admin-role="isAdmin"
      :allow-manager-role="isAdmin"
      @close="showUserModal = false"
      @submit="saveUser"
    />

    <ToastStack :items="toasts" />
    <ChatBot />
  </div>
</template>

<style scoped>
.manager-page {
  min-height: 100vh;
  /* Deep indigo fading into a muted slate-purple */
  background: linear-gradient(135deg, #1e1b4b 0%, #2e1065 100%);
  padding: 1rem;
  transition: background 0.3s ease;
}

.manager-shell {
  max-width: 80rem;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.manager-layout {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.manager-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.manager-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.manager-toolbar {
  border-radius: 1rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  animation: floatIn 350ms ease-out;
}

.manager-input {
  width: 100%;
  box-sizing: border-box;
  border: none;
  border-radius: 0.75rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.8);
  color: #1e293b;
}

.manager-button {
  border: none;
  border-radius: 0.75rem;
  padding: 0.5rem 1rem;
  color: #ffffff;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 200ms ease;
}

.manager-button--create-task {
  background: #10b981;
}

.manager-button--create-task:hover {
  background: #059669;
}

.manager-button--add-user {
  background: #4f46e5;
}

.manager-button--add-user:hover {
  background: #4338ca;
}

.manager-task-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 1rem;
}

.manager-users-table-wrap {
  border-radius: 1rem;
  padding: 1rem;
  animation: floatIn 350ms ease-out;
  overflow: auto;
}

.manager-users-title {
  margin: 0 0 0.75rem;
  font-size: 1.125rem;
  line-height: 1.75rem;
  font-weight: 600;
  color: #0f172a;
}

.manager-users-table {
  width: 100%;
  min-width: 48.75rem;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.manager-users-head-row {
  color: #475569;
  border-bottom: 1px solid rgba(226, 232, 240, 0.5);
}

.manager-users-cell {
  padding: 0.5rem 0;
}

.manager-users-cell--capitalize {
  text-transform: capitalize;
}

.manager-users-row {
  border-bottom: 1px solid rgba(226, 232, 240, 0.3);
  color: #1e293b;
}

.manager-status-chip {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  line-height: 1rem;
  border-radius: 9999px;
}

.manager-status-chip--active {
  background: #d1fae5;
  color: #047857;
}

.manager-status-chip--inactive {
  background: #fee2e2;
  color: #b91c1c;
}

.manager-users-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.manager-action {
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  line-height: 1rem;
  font-weight: 600;
  cursor: pointer;
}

.manager-action--edit {
  background: #e0e7ff;
  color: #4338ca;
}

.manager-action--deactivate {
  background: #fef3c7;
  color: #b45309;
}

.manager-action--activate {
  background: #d1fae5;
  color: #047857;
}

.manager-action--delete {
  background: #fee2e2;
  color: #b91c1c;
}

.manager-users-empty {
  padding: 1.5rem 0;
  text-align: center;
  color: #64748b;
}

.manager-category-check-wrap {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.manager-category-check {
  width: 1rem;
  height: 1rem;
}

.manager-analytics-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.manager-analytics-kpi {
  border-radius: 1rem;
  padding: 0.85rem;
}

.manager-analytics-kpi__label {
  margin: 0;
  font-size: 0.8rem;
}

.manager-analytics-kpi__value {
  margin: 0.25rem 0 0;
  font-size: 1.4rem;
  font-weight: 700;
  color: #0f172a;
}

.manager-analytics-cards {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 1rem;
}

.manager-analytics-card {
  border-radius: 1rem;
  padding: 1rem;
}

.manager-analytics-card--wide {
  grid-column: span 1;
}

.manager-analytics-title {
  margin: 0 0 0.75rem;
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
}

.manager-analytics-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.manager-analytics-list__item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.65rem;
  border-radius: 0.65rem;
  background: rgba(255, 255, 255, 0.68);
  color: #1e293b;
}

.manager-analytics-donut {
  height: 15rem;
  width: 100%;
}

.manager-analytics-loading {
  border-radius: 1rem;
  padding: 0.85rem;
  color: #334155;
}

/* --- Dark Mode Integrations --- */
:global(html.dark) .manager-page {
  /* Deepen the shadows for Dark Mode */
  background: linear-gradient(135deg, #0f172a 0%, #170f2e 100%);
}

:global(html.dark) .manager-input {
  background: #334155;
  color: #f1f5f9;
}

:global(html.dark) .manager-users-title {
  color: #f1f5f9;
}

:global(html.dark) .manager-users-head-row {
  color: #cbd5e1;
}

:global(html.dark) .manager-users-row {
  color: #f1f5f9;
}

:global(html.dark) .manager-analytics-kpi__value,
:global(html.dark) .manager-analytics-title {
  color: #f8fafc;
}

:global(html.dark) .manager-analytics-list__item {
  background: rgba(30, 41, 59, 0.72);
  color: #e2e8f0;
}

:global(html.dark) .manager-analytics-loading {
  color: #cbd5e1;
}

@media (min-width: 640px) {
  .manager-task-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .manager-analytics-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (min-width: 768px) {
  .manager-page {
    padding: 1.5rem;
  }

  .manager-layout {
    flex-direction: row;
  }

  .manager-analytics-cards {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .manager-analytics-card--wide {
    grid-column: span 2;
  }

  .manager-toolbar {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }

  .manager-input {
    max-width: 28rem;
  }
}

@media (min-width: 1280px) {
  .manager-task-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
