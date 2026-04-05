<script setup>
import { computed, onMounted, ref, watch } from "vue";
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
import { translationService } from "../../services/translationService";

const router = useRouter();

const currentUser = ref({ name: "", role: "staff", email: "" });
const darkMode = ref(localStorage.getItem("ui_theme") === "dark");
const notificationOpen = ref(false);
const notifications = ref([]);

const baseUiText = {
  myTasks: "My Tasks",
  translationView: "Translation View",
  all: "All",
  pending: "Pending",
  inProgress: "In Progress",
  completed: "Completed",
  english: "English",
  hindi: "Hindi",
  kannada: "Kannada",
  hello: "Hello",
  subtitleFallback: "Staff workspace with translated task descriptions",
  profileError: "Could not load user profile.",
  tasksError: "Could not load tasks.",
  notificationsError: "Could not load notifications.",
  statusUpdated: "Task status updated.",
  statusUpdateError: "Failed to update status.",
  markReadError: "Could not mark notification as read.",
  translatingTitle: "Turning words into your language...",
  translatingSubtitle: "Please hold tight while we localize your workspace.",
};

const uiText = ref({ ...baseUiText });
const uiTranslationCache = ref({ en: { ...baseUiText } });

const sidebarItems = computed(() => [
  { key: "tasks", label: uiText.value.myTasks },
  { key: "translation", label: uiText.value.translationView },
]);
const activePanel = ref("tasks");

const loading = ref(true);
const isTranslating = ref(false);
const tasks = ref([]);
const selectedLanguage = ref("en");
const selectedFilter = ref("All");
const translationRequestId = ref(0);

const toasts = ref([]);
const pushToast = (message, type = "info") => {
  const id = Date.now() + Math.floor(Math.random() * 1000);
  toasts.value.push({ id, message, type });
  setTimeout(() => {
    toasts.value = toasts.value.filter((toast) => toast.id !== id);
  }, 2600);
};

const filters = computed(() => [
  uiText.value.all,
  uiText.value.pending,
  uiText.value.inProgress,
  uiText.value.completed,
]);

const statusFilterMap = computed(() => ({
  [uiText.value.all]: "All",
  [uiText.value.pending]: "Pending",
  [uiText.value.inProgress]: "In Progress",
  [uiText.value.completed]: "Completed",
}));

const navbarTitle = computed(() => {
  return currentUser.value.name
    ? `${uiText.value.hello} ${currentUser.value.name}`
    : uiText.value.hello;
});

const navbarSubtitle = computed(() => {
  const roleLabel = (currentUser.value.role || "staff").toUpperCase();
  if (currentUser.value.email) {
    return `${roleLabel} • ${currentUser.value.email}`;
  }
  return uiText.value.subtitleFallback;
});

const loadCurrentUser = async () => {
  try {
    currentUser.value = await userService.getMe();
  } catch (error) {
    pushToast(uiText.value.profileError, "error");
  }
};

const filteredTasks = computed(() => {
  const normalizedFilter = statusFilterMap.value[selectedFilter.value] || "All";
  if (normalizedFilter === "All") {
    return tasks.value;
  }
  return tasks.value.filter((task) => task.status === normalizedFilter);
});

const loadTasks = async () => {
  loading.value = true;
  try {
    tasks.value = await taskService.getAssigned(selectedLanguage.value);
  } catch (error) {
    pushToast(uiText.value.tasksError, "error");
  } finally {
    loading.value = false;
  }
};

const loadNotifications = async () => {
  try {
    notifications.value = await notificationService.getUnread();
  } catch (error) {
    pushToast(uiText.value.notificationsError, "error");
  }
};

const updateTaskStatus = async (taskId, status) => {
  try {
    await taskService.updateStatus(taskId, status);
    tasks.value = tasks.value.map((task) =>
      task.id === taskId ? { ...task, status } : task
    );
    pushToast(uiText.value.statusUpdated, "success");
  } catch (error) {
    pushToast(uiText.value.statusUpdateError, "error");
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
    pushToast(uiText.value.markReadError, "error");
  }
};

const loadUiTranslations = async () => {
  const language = selectedLanguage.value;
  if (language === "en") {
    uiText.value = { ...baseUiText };
    return;
  }

  if (uiTranslationCache.value[language]) {
    uiText.value = uiTranslationCache.value[language];
    return;
  }

  try {
    const translated = await translationService.translateUI(baseUiText, language);
    const merged = { ...baseUiText, ...translated };
    uiTranslationCache.value[language] = merged;
    uiText.value = merged;
  } catch (_error) {
    uiText.value = { ...baseUiText };
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
  await loadUiTranslations();
  await Promise.all([loadCurrentUser(), loadTasks(), loadNotifications()]);
});

watch(selectedLanguage, async () => {
  const requestId = Date.now();
  translationRequestId.value = requestId;
  isTranslating.value = true;

  try {
    await loadUiTranslations();
    selectedFilter.value = uiText.value.all;
    await loadTasks();
  } finally {
    if (translationRequestId.value === requestId) {
      isTranslating.value = false;
    }
  }
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
              <option value="en">{{ uiText.english }}</option>
              <option value="hi">{{ uiText.hindi }}</option>
              <option value="kn">{{ uiText.kannada }}</option>
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

    <transition name="translate-overlay-fade">
      <div v-if="isTranslating" class="translate-overlay">
        <div class="translate-overlay__card glass-panel">
          <div class="translate-overlay__spinner" />
          <h3 class="translate-overlay__title">{{ uiText.translatingTitle }}</h3>
          <p class="translate-overlay__subtitle">{{ uiText.translatingSubtitle }}</p>
        </div>
      </div>
    </transition>
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

.translate-overlay-fade-enter-active,
.translate-overlay-fade-leave-active {
  transition: opacity 0.2s ease;
}

.translate-overlay-fade-enter-from,
.translate-overlay-fade-leave-to {
  opacity: 0;
}

.translate-overlay {
  position: fixed;
  inset: 0;
  z-index: 70;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.25);
  backdrop-filter: blur(5px);
  padding: 1rem;
}

.translate-overlay__card {
  max-width: 26rem;
  width: 100%;
  border-radius: 1rem;
  padding: 1.25rem;
  text-align: center;
}

.translate-overlay__spinner {
  width: 2.5rem;
  height: 2.5rem;
  margin: 0 auto 0.75rem;
  border-radius: 9999px;
  border: 3px solid rgba(79, 70, 229, 0.2);
  border-top-color: #4f46e5;
  animation: spin 0.9s linear infinite;
}

.translate-overlay__title {
  margin: 0;
  font-size: 1.1rem;
  color: #0f172a;
}

.translate-overlay__subtitle {
  margin: 0.5rem 0 0;
  font-size: 0.9rem;
  color: #334155;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

:global(html.dark) .translate-overlay__title {
  color: #f8fafc;
}

:global(html.dark) .translate-overlay__subtitle {
  color: #cbd5e1;
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
