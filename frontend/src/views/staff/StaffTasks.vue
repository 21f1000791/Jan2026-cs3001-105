<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import AppNavbar from "../../components/ui/AppNavbar.vue";
import AppSidebar from "../../components/ui/AppSidebar.vue";
import TaskCard from "../../components/tasks/TaskCard.vue";
import SkeletonCard from "../../components/ui/SkeletonCard.vue";
import ToastStack from "../../components/ui/ToastStack.vue";
import { authService } from "../../services/authService";
import { dashboardService } from "../../services/dashboardService";
import { taskService } from "../../services/taskService";
import { notificationService } from "../../services/notificationService";
import { userService } from "../../services/userService";

const router = useRouter();

const currentUser = ref({ name: "", role: "staff", email: "" });
const darkMode = ref(localStorage.getItem("ui_theme") === "dark");
const notificationOpen = ref(false);
const notifications = ref([]);

// ==========================================
// 1. HARDCODED UI TRANSLATION DICTIONARY
// ==========================================
const uiTranslations = {
  en: {
    myTasks: "My Tasks",
    analyticsView: "Analytics View",
    personalInsights: "Personal Insights",
    assignedTasks: "Assigned Tasks",
    overdueTasks: "Overdue Tasks",
    completionRate: "Completion Rate",
    analyticsSummary: "Your analytics are based only on tasks assigned to you.",
    all: "All",
    pending: "Pending",
    inProgress: "In Progress",
    completed: "Completed",
    english: "English",
    hindi: "Hindi",
    kannada: "Kannada",
    hello: "Hello",
    staffRole: "STAFF",
    darkMode: "Dark Mode",
    lightMode: "Light Mode",
    notifications: "Notifications",
    logout: "Logout",
    workspace: "Workspace",
    inbox: "Inbox",
    noUnreadNotifications: "No unread notifications.",
    markAsRead: "Mark as read",
    subtitleFallback: "Staff workspace with translated task descriptions",
    profileError: "Could not load user profile.",
    tasksError: "Could not load tasks.",
    notificationsError: "Could not load notifications.",
    statusUpdated: "Task status updated.",
    statusUpdateError: "Failed to update status.",
    markReadError: "Could not mark notification as read.",
    translatingTitle: "Turning words into your language...",
    translatingSubtitle: "Please hold tight while we localize your workspace.",
  },
  hi: {
    myTasks: "मेरे कार्य",
    analyticsView: "विश्लेषण दृश्य",
    personalInsights: "व्यक्तिगत विश्लेषण",
    assignedTasks: "सौंपे गए कार्य",
    overdueTasks: "अतिदेय कार्य",
    completionRate: "पूर्णता दर",
    analyticsSummary: "आपका विश्लेषण केवल आपको सौंपे गए कार्यों पर आधारित है।",
    all: "सभी",
    pending: "लंबित",
    inProgress: "प्रगति पर",
    completed: "पूर्ण",
    english: "अंग्रेजी",
    hindi: "हिंदी",
    kannada: "कन्नड़",
    hello: "नमस्ते",
    staffRole: "कर्मचारी",
    darkMode: "डार्क मोड",
    lightMode: "लाइट मोड",
    notifications: "सूचनाएं",
    logout: "लॉगआउट",
    workspace: "कार्यस्थान",
    inbox: "इनबॉक्स",
    noUnreadNotifications: "कोई अपठित सूचना नहीं है।",
    markAsRead: "पढ़ा हुआ चिह्नित करें",
    subtitleFallback: "अनुवादित कार्य विवरण के साथ कर्मचारी कार्यक्षेत्र",
    profileError: "उपयोगकर्ता प्रोफ़ाइल लोड नहीं की जा सकी।",
    tasksError: "कार्य लोड नहीं किए जा सके।",
    notificationsError: "सूचनाएं लोड नहीं की जा सकीं।",
    statusUpdated: "कार्य की स्थिति अपडेट की गई।",
    statusUpdateError: "स्थिति अपडेट करने में विफल।",
    markReadError: "सूचना को पढ़ा हुआ चिह्नित नहीं किया जा सका।",
    translatingTitle: "शब्दों को आपकी भाषा में बदल रहे हैं...",
    translatingSubtitle: "कृपया प्रतीक्षा करें जब तक हम आपके कार्यक्षेत्र का अनुवाद करते हैं।",
  },
  kn: {
    myTasks: "ನನ್ನ ಕಾರ್ಯಗಳು",
    analyticsView: "ವಿಶ್ಲೇಷಣೆ ನೋಟ",
    personalInsights: "ವೈಯಕ್ತಿಕ ವಿಶ್ಲೇಷಣೆ",
    assignedTasks: "ನಿಮಗೆ ನಿಯೋಜಿಸಿದ ಕಾರ್ಯಗಳು",
    overdueTasks: "ಮೀರಿದ ಅವಧಿಯ ಕಾರ್ಯಗಳು",
    completionRate: "ಪೂರ್ಣಗೊಳಿಸುವ ಪ್ರಮಾಣ",
    analyticsSummary: "ನಿಮ್ಮ ವಿಶ್ಲೇಷಣೆ ನಿಮಗೆ ನಿಯೋಜಿಸಿದ ಕಾರ್ಯಗಳ ಮೇಲೆ ಮಾತ್ರ ಆಧಾರಿತವಾಗಿದೆ.",
    all: "ಎಲ್ಲಾ",
    pending: "ಬಾಕಿ ಉಳಿದಿದೆ",
    inProgress: "ಪ್ರಗತಿಯಲ್ಲಿದೆ",
    completed: "ಪೂರ್ಣಗೊಂಡಿದೆ",
    english: "ಇಂಗ್ಲಿಷ್",
    hindi: "ಹಿಂದಿ",
    kannada: "ಕನ್ನಡ",
    hello: "ನಮಸ್ಕಾರ",
    staffRole: "ಸಿಬ್ಬಂದಿ",
    darkMode: "ಡಾರ್ಕ್ ಮೋಡ್",
    lightMode: "ಲೈಟ್ ಮೋಡ್",
    notifications: "ಅಧಿಸೂಚನೆಗಳು",
    logout: "ಲಾಗ್ ಔಟ್",
    workspace: "ಕಾರ್ಯಸ್ಥಳ",
    inbox: "ಇನ್‌ಬಾಕ್ಸ್",
    noUnreadNotifications: "ಓದದ ಅಧಿಸೂಚನೆಗಳಿಲ್ಲ.",
    markAsRead: "ಓದಲಾಗಿದೆ ಎಂದು ಗುರುತಿಸಿ",
    subtitleFallback: "ಅನುವಾದಿತ ಕಾರ್ಯ ವಿವರಣೆಗಳೊಂದಿಗೆ ಸಿಬ್ಬಂದಿ ಕಾರ್ಯಕ್ಷೇತ್ರ",
    profileError: "ಬಳಕೆದಾರರ ಪ್ರೊಫೈಲ್ ಲೋಡ್ ಮಾಡಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.",
    tasksError: "ಕಾರ್ಯಗಳನ್ನು ಲೋಡ್ ಮಾಡಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.",
    notificationsError: "ಸೂಚನೆಗಳನ್ನು ಲೋಡ್ ಮಾಡಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.",
    statusUpdated: "ಕಾರ್ಯದ ಸ್ಥಿತಿಯನ್ನು ನವೀಕರಿಸಲಾಗಿದೆ.",
    statusUpdateError: "ಸ್ಥಿತಿಯನ್ನು ನವೀಕರಿಸಲು ವಿಫಲವಾಗಿದೆ.",
    markReadError: "ಸೂಚನೆಯನ್ನು ಓದಲಾಗಿದೆ ಎಂದು ಗುರುತಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.",
    translatingTitle: "ಪದಗಳನ್ನು ನಿಮ್ಮ ಭಾಷೆಗೆ ಬದಲಾಯಿಸಲಾಗುತ್ತಿದೆ...",
    translatingSubtitle: "ನಿಮ್ಮ ಕಾರ್ಯಕ್ಷೇತ್ರವನ್ನು ನಾವು ಸ್ಥಳೀಕರಿಸುವವರೆಗೆ ದಯವಿಟ್ಟು ನಿರೀಕ್ಷಿಸಿ.",
  }
};

const selectedLanguage = ref("en");

const uiText = computed(() => uiTranslations[selectedLanguage.value] || uiTranslations.en);

const sidebarItems = computed(() => [
  { key: "tasks", label: uiText.value.myTasks },
  { key: "analytics", label: uiText.value.analyticsView },
]);
const activePanel = ref("tasks");

const loading = ref(true);
const isTranslating = ref(false);
const tasks = ref([]);
const lastAssignedMeta = ref({});
const selectedFilter = ref("All");
const translationRequestId = ref(0);
const analyticsLoading = ref(false);
const staffMetrics = ref({
  assigned: 0,
  completed: 0,
  pending: 0,
  overdue: 0,
  completionRate: 0,
});

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

const translatedDisplayName = computed(() => {
  const currentName = (currentUser.value.name || "").trim();
  if (!currentName) {
    return "";
  }

  const localizedNames = {
    hi: {
      "Staff One": "स्टाफ वन",
      "Staff Two": "स्टाफ टू",
      "Manager One": "मैनेजर वन",
    },
    kn: {
      "Staff One": "ಸ್ಟಾಫ್ ಒನ್",
      "Staff Two": "ಸ್ಟಾಫ್ ಟು",
      "Manager One": "ಮ್ಯಾನೇಜರ್ ಒನ್",
    },
  };

  return localizedNames[selectedLanguage.value]?.[currentName] || currentName;
});

const navbarTitle = computed(() => {
  return currentUser.value.name
    ? `${uiText.value.hello} ${translatedDisplayName.value}`
    : uiText.value.hello;
});

const navbarSubtitle = computed(() => {
  const roleLabel =
    (currentUser.value.role || "staff").toLowerCase() === "staff"
      ? uiText.value.staffRole
      : (currentUser.value.role || "staff").toUpperCase();
  if (currentUser.value.email) {
    return `${roleLabel} • ${currentUser.value.email}`;
  }
  return uiText.value.subtitleFallback;
});

const loadCurrentUser = async () => {
  try {
    const response = await userService.getMe();
    currentUser.value = response.user ? response.user : response;
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

const analyticsCards = computed(() => [
  { key: "assigned", label: uiText.value.assignedTasks, value: staffMetrics.value.assigned },
  { key: "completed", label: uiText.value.completed, value: staffMetrics.value.completed },
  { key: "pending", label: uiText.value.pending, value: staffMetrics.value.pending },
  { key: "overdue", label: uiText.value.overdueTasks, value: staffMetrics.value.overdue },
  {
    key: "completionRate",
    label: uiText.value.completionRate,
    value: `${Number(staffMetrics.value.completionRate || 0).toFixed(1)}%`,
  },
]);

const completionRatio = computed(() => {
  const value = Number(staffMetrics.value.completionRate || 0);
  if (value < 0) {
    return 0;
  }
  if (value > 100) {
    return 100;
  }
  return value;
});

// Fetches ALL tasks when the global UI language changes
const loadTasks = async () => {
  loading.value = true;
  try {
    const data = await taskService.getAssigned(selectedLanguage.value);
    lastAssignedMeta.value = data.meta || {};
    const rawTasks = data.items || data;
    
    // Explicitly set the activeLang so the TaskCard buttons highlight correctly on initial load
    tasks.value = rawTasks.map(t => ({
      ...t,
      activeLang: selectedLanguage.value 
    }));
  } catch (error) {
    pushToast(uiText.value.tasksError, "error");
  } finally {
    loading.value = false;
  }
};

// FIXED: Bulletproof single task translation
const translateSingleTask = async (taskId, targetLang) => {
  try {
    const token = localStorage.getItem("auth_token") || "";
    const response = await fetch(`http://127.0.0.1:5000/api/tasks/${taskId}?lang=${targetLang}`, {
      headers: { 
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      const translatedTask = data.task || data; 
      
      const idx = tasks.value.findIndex(t => t.id === taskId);
      if (idx !== -1) {
        // 1. Explicitly mutate the properties to guarantee Vue reactivity inside TaskCard
        const taskRef = tasks.value[idx];
        
        // 2. If switching to English, wipe out the translated fields so it falls back to the original text
        if (targetLang === 'en') {
          taskRef.translated_title = null;
          taskRef.translated_description = null;
          taskRef.translated_category = null;
          taskRef.title = translatedTask.title || taskRef.title;
          taskRef.category = translatedTask.category || taskRef.category;
          taskRef.description = {
            en: translatedTask.description || "",
            hi: "",
            kn: "",
          };
        } else {
          taskRef.translated_title = translatedTask.translated_title;
          taskRef.translated_description = translatedTask.translated_description;
          taskRef.translated_category = translatedTask.translated_category;
          taskRef.title = translatedTask.translated_title || translatedTask.title || taskRef.title;
          taskRef.category = translatedTask.translated_category || translatedTask.category || taskRef.category;
          taskRef.description = {
            en: translatedTask.translated_description || translatedTask.description || "",
            hi: "",
            kn: "",
          };
        }
        
        // 3. Update the activeLang so the TaskCard highlights the button you just clicked
        taskRef.activeLang = targetLang;
      }
    } else {
      pushToast(uiText.value.tasksError, "error");
    }
  } catch (error) {
    pushToast(uiText.value.tasksError, "error");
  }
};

const loadNotifications = async () => {
  try {
    notifications.value = await notificationService.getUnread();
  } catch (error) {
    pushToast(uiText.value.notificationsError, "error");
  }
};

const loadStaffAnalytics = async () => {
  analyticsLoading.value = true;
  try {
    const dashboard = await dashboardService.getStaffDashboard();
    staffMetrics.value = {
      assigned: Number(dashboard.metrics?.assigned || 0),
      completed: Number(dashboard.metrics?.completed || 0),
      pending: Number(dashboard.metrics?.pending || 0),
      overdue: Number(dashboard.metrics?.overdue || 0),
      completionRate: Number(dashboard.metrics?.completionRate || 0),
    };
  } catch (error) {
    pushToast(uiText.value.tasksError, "error");
  } finally {
    analyticsLoading.value = false;
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

const toggleTheme = () => {
  darkMode.value = !darkMode.value;
  document.documentElement.classList.toggle("dark", darkMode.value);
  localStorage.setItem("ui_theme", darkMode.value ? "dark" : "light");
};

const logout = async () => {
  localStorage.removeItem("auth_token");
  localStorage.removeItem("user_role");
  try {
    await authService.logout();
  } catch(e) {
    console.warn("Backend logout failed, proceeding locally.");
  } finally {
    router.push("/login");
  }
};

onMounted(async () => {
  document.documentElement.classList.toggle("dark", darkMode.value);
  await Promise.all([loadCurrentUser(), loadTasks(), loadNotifications(), loadStaffAnalytics()]);
});

// Triggers ONLY when the top right global language dropdown is changed
watch(selectedLanguage, async () => {
  const requestId = Date.now();
  const requestStart = Date.now();
  translationRequestId.value = requestId;
  isTranslating.value = true;

  try {
    selectedFilter.value = uiText.value.all;
    await loadTasks(); 
  } finally {
    if (translationRequestId.value === requestId) {
      const usedLiveTranslationApi = Boolean(lastAssignedMeta.value?.translation_api_used);

      if (usedLiveTranslationApi) {
        // Dynamic duration: hide immediately after API returns when retranslation was needed.
        isTranslating.value = false;
      } else {
        // Cache-only duration: keep overlay for a fixed total of 2 seconds.
        const elapsed = Date.now() - requestStart;
        const remaining = Math.max(0, 1000 - elapsed);
        setTimeout(() => {
          if (translationRequestId.value === requestId) {
            isTranslating.value = false;
          }
        }, remaining);
      }
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
        :ui-text="uiText"
        :notifications="notifications"
        :notification-open="notificationOpen"
        :dark-mode="darkMode"
        @toggle-theme="toggleTheme"
        @toggle-notifications="notificationOpen = !notificationOpen"
        @mark-notification-read="markNotificationRead"
        @logout="logout"
      />

      <div class="staff-layout">
        <AppSidebar v-model="activePanel" :items="sidebarItems" :label="uiText.workspace" />

        <section class="staff-content">
          <template v-if="activePanel === 'tasks'">
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
                @set-language="translateSingleTask(task.id, $event)"
              />
            </div>
          </template>

          <template v-else>
            <div class="staff-analytics-panel">
              <div class="staff-analytics-summary glass-panel">
                <h2 class="staff-analytics-title">{{ uiText.personalInsights }}</h2>
                <p class="staff-analytics-subtitle">{{ uiText.analyticsSummary }}</p>
              </div>

              <div class="staff-analytics-grid">
                <div
                  v-for="item in analyticsCards"
                  :key="item.key"
                  class="staff-analytics-card glass-panel"
                >
                  <p class="staff-analytics-card__label">{{ item.label }}</p>
                  <p class="staff-analytics-card__value">{{ item.value }}</p>
                </div>
              </div>

              <div class="staff-analytics-progress glass-panel">
                <div class="staff-analytics-progress__head">
                  <span>{{ uiText.completionRate }}</span>
                  <strong>{{ Number(staffMetrics.completionRate || 0).toFixed(1) }}%</strong>
                </div>
                <div class="staff-analytics-progress__track">
                  <div class="staff-analytics-progress__fill" :style="{ width: `${completionRatio}%` }" />
                </div>
              </div>

              <div v-if="analyticsLoading" class="staff-analytics-loading glass-panel">
                Loading analytics...
              </div>
            </div>
          </template>
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

.staff-analytics-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.staff-analytics-summary {
  border-radius: 1rem;
  padding: 1rem;
}

.staff-analytics-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
}

.staff-analytics-subtitle {
  margin: 0.45rem 0 0;
  color: #334155;
  font-size: 0.92rem;
}

.staff-analytics-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 0.85rem;
}

.staff-analytics-card {
  border-radius: 1rem;
  padding: 0.95rem 1rem;
}

.staff-analytics-card__label {
  margin: 0;
  color: #475569;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.staff-analytics-card__value {
  margin: 0.3rem 0 0;
  color: #0f172a;
  font-size: 1.35rem;
  font-weight: 700;
}

.staff-analytics-progress {
  border-radius: 1rem;
  padding: 1rem;
}

.staff-analytics-progress__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #1e293b;
  font-weight: 600;
  margin-bottom: 0.6rem;
}

.staff-analytics-progress__track {
  height: 0.75rem;
  width: 100%;
  border-radius: 9999px;
  background: rgba(15, 23, 42, 0.1);
  overflow: hidden;
}

.staff-analytics-progress__fill {
  height: 100%;
  border-radius: 9999px;
  background: linear-gradient(90deg, #22c55e 0%, #3b82f6 100%);
  transition: width 250ms ease;
}

.staff-analytics-loading {
  border-radius: 1rem;
  padding: 0.9rem 1rem;
  color: #334155;
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

:global(html.dark) .staff-analytics-title,
:global(html.dark) .staff-analytics-card__value,
:global(html.dark) .staff-analytics-progress__head {
  color: #f8fafc;
}

:global(html.dark) .staff-analytics-subtitle,
:global(html.dark) .staff-analytics-card__label,
:global(html.dark) .staff-analytics-loading {
  color: #cbd5e1;
}

:global(html.dark) .staff-analytics-progress__track {
  background: rgba(148, 163, 184, 0.22);
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

  .staff-analytics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1280px) {
  .tasks-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
