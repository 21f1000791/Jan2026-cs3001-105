<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import AppNavbar from "../../components/ui/AppNavbar.vue";
import AppSidebar from "../../components/ui/AppSidebar.vue";
import TaskCard from "../../components/tasks/TaskCard.vue";
import SkeletonCard from "../../components/ui/SkeletonCard.vue";
import ToastStack from "../../components/ui/ToastStack.vue";
import { authService } from "../../services/authService";
import { taskService } from "../../services/taskService";
import { notificationService } from "../../services/notificationService";
import { userService } from "../../services/userService";

const router = useRouter();

const currentUser = ref({ name: "", role: "staff", email: "" });
const darkMode = ref(localStorage.getItem("ui_theme") === "dark");
const notificationOpen = ref(false);
const notifications = ref([]);

const sidebarItems = [
  { key: "tasks", label: "My Tasks" },
  { key: "translation", label: "Translation View" },
];
const activePanel = ref("tasks");

const loading = ref(true);
const tasks = ref([]);
const selectedLanguage = ref("en");
const selectedFilter = ref("All");

const toasts = ref([]);
const pushToast = (message, type = "info") => {
  const id = Date.now() + Math.floor(Math.random() * 1000);
  toasts.value.push({ id, message, type });
  setTimeout(() => {
    toasts.value = toasts.value.filter((toast) => toast.id !== id);
  }, 2600);
};

const filters = ["All", "Pending", "In Progress", "Completed"];

const navbarTitle = computed(() => {
  return currentUser.value.name ? `Hello ${currentUser.value.name}` : "Hello";
});

const navbarSubtitle = computed(() => {
  const roleLabel = (currentUser.value.role || "staff").toUpperCase();
  if (currentUser.value.email) {
    return `${roleLabel} • ${currentUser.value.email}`;
  }
  return "Staff workspace with translated task descriptions";
});

const loadCurrentUser = async () => {
  try {
    currentUser.value = await userService.getMe();
  } catch (error) {
    pushToast("Could not load user profile.", "error");
  }
};

const filteredTasks = computed(() => {
  if (selectedFilter.value === "All") {
    return tasks.value;
  }
  return tasks.value.filter((task) => task.status === selectedFilter.value);
});

const loadTasks = async () => {
  loading.value = true;
  try {
    tasks.value = await taskService.getAssigned();
  } catch (error) {
    pushToast("Could not load tasks.", "error");
  } finally {
    loading.value = false;
  }
};

const loadNotifications = async () => {
  try {
    notifications.value = await notificationService.getUnread();
  } catch (error) {
    pushToast("Could not load notifications.", "error");
  }
};

const updateTaskStatus = async (taskId, status) => {
  try {
    await taskService.updateStatus(taskId, status);
    tasks.value = tasks.value.map((task) =>
      task.id === taskId ? { ...task, status } : task
    );
    pushToast("Task status updated.", "success");
  } catch (error) {
    pushToast("Failed to update status.", "error");
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
  await Promise.all([loadCurrentUser(), loadTasks(), loadNotifications()]);
});
</script>

<template>
  <div class="staff-page">
    <div class="staff-shell">
      <AppNavbar
        :title="navbarTitle"
        :subtitle="navbarSubtitle"
        :notifications="notifications"
        :notification-open="notificationOpen"
        :dark-mode="darkMode"
        @toggle-theme="toggleTheme"
        @toggle-notifications="notificationOpen = !notificationOpen"
        @mark-notification-read="markNotificationRead"
        @logout="logout"
      />

      <div class="staff-layout">
        <AppSidebar v-model="activePanel" :items="sidebarItems" />

        <section class="staff-content">
          <div class="filters-panel glass-panel">
            <button
              v-for="filter in filters"
              :key="filter"
              @click="selectedFilter = filter"
              class="filter-button"
              :class="selectedFilter === filter
                ? 'filter-button active'
                : 'filter-button inactive'"
            >
              {{ filter }}
            </button>

            <select
              v-model="selectedLanguage"
              class="language-select"
            >
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="kn">Kannada</option>
            </select>
          </div>

          <div class="tasks-grid">
            <template v-if="loading">
              <SkeletonCard v-for="idx in 6" :key="idx" />
            </template>

            <TaskCard
              v-for="task in filteredTasks"
              v-else
              :key="task.id"
              :task="task"
              :ui-language="selectedLanguage"
              @status-change="updateTaskStatus(task.id, $event)"
              @set-language="selectedLanguage = $event"
            />
          </div>
        </section>
      </div>
    </div>

    <ToastStack :items="toasts" />
  </div>
</template>

<style scoped>
.staff-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #a8e063 0%, #f0ff00 100%);
  padding: 1rem;
}

.staff-shell {
  max-width: 80rem;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.staff-layout {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.staff-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.filters-panel {
  border-radius: 1rem;
  padding: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  animation: floatIn 350ms ease-out;
}

.filter-button {
  border-radius: 9999px;
  padding: 0.375rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
}

.filter-button.active {
  background: #4f46e5;
  color: #fff;
}

.filter-button.inactive {
  background: rgba(255, 255, 255, 0.8);
  color: #1e293b;
}

:global(html.dark) .filter-button.inactive {
  background: #334155;
  color: #f1f5f9;
}

.language-select {
  margin-left: auto;
  border-radius: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
  border: 1px solid rgba(100, 116, 139, 0.25);
  color: #0f172a;
}

:global(html.dark) .language-select {
  background: #334155;
  color: #f1f5f9;
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 1rem;
}

@media (min-width: 768px) {
  .staff-page {
    padding: 1.5rem;
  }

  .staff-layout {
    flex-direction: row;
  }
}

@media (min-width: 640px) {
  .tasks-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1280px) {
  .tasks-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
