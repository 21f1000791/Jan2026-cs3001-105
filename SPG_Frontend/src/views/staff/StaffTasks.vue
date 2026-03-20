<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
const router = useRouter();
const USE_REAL_BACKEND = false;
const uiTranslations = {
  en: {
    hello: "Hello",
    role: "Staff Member",
    alerts: "Alerts",
    notifications: "Notifications",
    terminate: "Terminate Account",
    logout: "Logout",
    sysAlerts: "System Alerts",
    noOverdue: "No overdue tasks. Great job!",
    inbox: "Inbox Notifications",
    caughtUp: "You're all caught up!",
    markRead: "Mark Read",
    filters: {
      All: "All",
      Pending: "Pending",
      "In Progress": "In Progress",
      Completed: "Completed",
    },
    due: "Due",
    overdueAlert: "(Overdue!)",
    lastUpdated: "Last Updated",
    markPending: "Mark as Pending",
    markInProgress: "Mark as In Progress",
    markCompleted: "Mark as Completed",
  },
  hi: {
    hello: "नमस्ते",
    role: "कर्मचारी",
    alerts: "अलर्ट",
    notifications: "सूचनाएं",
    terminate: "खाता समाप्त करें",
    logout: "लॉग आउट",
    sysAlerts: "सिस्टम अलर्ट",
    noOverdue: "कोई अतिदेय कार्य नहीं। बहुत बढ़िया!",
    inbox: "इनबॉक्स सूचनाएं",
    caughtUp: "आपने सब पढ़ लिया है!",
    markRead: "पढ़ा हुआ चिह्नित करें",
    filters: {
      All: "सभी",
      Pending: "लंबित",
      "In Progress": "प्रगति पर",
      Completed: "पूर्ण",
    },
    due: "देय तिथि",
    overdueAlert: "(अतिदेय!)",
    lastUpdated: "अंतिम अपडेट",
    markPending: "लंबित चिह्नित करें",
    markInProgress: "प्रगति पर चिह्नित करें",
    markCompleted: "पूर्ण चिह्नित करें",
  },
  kn: {
    hello: "ನಮಸ್ಕಾರ",
    role: "ಸಿಬ್ಬಂದಿ",
    alerts: "ಎಚ್ಚರಿಕೆಗಳು",
    notifications: "ಸೂಚನೆಗಳು",
    terminate: "ಖಾತೆಯನ್ನು ಕೊನೆಗೊಳಿಸಿ",
    logout: "ಲಾಗ್ ಔಟ್",
    sysAlerts: "ಸಿಸ್ಟಮ್ ಎಚ್ಚರಿಕೆಗಳು",
    noOverdue: "ಯಾವುದೇ ಬಾಕಿ ಉಳಿದಿಲ್ಲ. ಒಳ್ಳೆಯ ಕೆಲಸ!",
    inbox: "ಇನ್‌ಬಾಕ್ಸ್ ಸೂಚನೆಗಳು",
    caughtUp: "ನೀವು ಎಲ್ಲವನ್ನೂ ಓದಿದ್ದೀರಿ!",
    markRead: "ಓದಲಾಗಿದೆ",
    filters: {
      All: "ಎಲ್ಲಾ",
      Pending: "ಬಾಕಿ ಉಳಿದಿದೆ",
      "In Progress": "ಪ್ರಗತಿಯಲ್ಲಿದೆ",
      Completed: "ಪೂರ್ಣಗೊಂಡಿದೆ",
    },
    due: "ಗಡುವು",
    overdueAlert: "(ಮಿತಿಮೀರಿದೆ!)",
    lastUpdated: "ಕೊನೆಯದಾಗಿ ನವೀಕರಿಸಲಾಗಿದೆ",
    markPending: "ಬಾಕಿ ಎಂದು ಗುರುತಿಸಿ",
    markInProgress: "ಪ್ರಗತಿಯಲ್ಲಿದೆ ಎಂದು ಗುರುತಿಸಿ",
    markCompleted: "ಪೂರ್ಣಗೊಂಡಿದೆ ಎಂದು ಗುರುತಿಸಿ",
  },
};
const currentUser = ref({ name: "Loading...", role: "", language: "en" });
const t = computed(
  () => uiTranslations[currentUser.value.language] || uiTranslations["en"]
);

const loadUserProfile = async () => {
  if (USE_REAL_BACKEND) {
    try {
      const response = await fetch("http://127.0.0.1:5000/api/users/me", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer DUMMY_TOKEN",
        },
      });

      if (response.ok) {
        currentUser.value = await response.json();
        if (!currentUser.value.language) currentUser.value.language = "en";
      }
    } catch (error) {
      console.error("Error connecting to Flask:", error);
    }
  } else {
    currentUser.value = {
      name: "Priyangshu Bhattacharyya",
      role: "Staff Member",
      language: "en",
    };
  }
};
const updateUILanguage = async (event) => {
  const newLang = event.target.value;
  currentUser.value.language = newLang;

  if (USE_REAL_BACKEND) {
    try {
      await fetch("http://127.0.0.1:5000/api/users/me/language", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer DUMMY_TOKEN",
        },
        body: JSON.stringify({ language: newLang }),
      });
    } catch (error) {
      console.error("Failed to save language preference:", error);
    }
  }
};
const tasks = ref([]);
const currentFilter = ref("All");
const filters = ["All", "Pending", "In Progress", "Completed"];
const loadTasks = async () => {
  if (USE_REAL_BACKEND) {
    try {
      const response = await fetch("http://127.0.0.1:5000/api/tasks/my-tasks", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer DUMMY_TOKEN",
        },
      });

      if (response.ok) {
        tasks.value = await response.json();
      }
    } catch (error) {
      console.error("Error connecting to Flask:", error);
    }
  } else {
    tasks.value = [
      {
        id: 1,
        title: "Update Frontend Routing Logic",
        category: "Development",
        dueDate: "2026-03-10",
        status: "In Progress",
        lastUpdated: "Not updated yet",
        description: {
          en: "Refactor the Vue router to handle dynamic tertiary user roles.",
          hi: "डायनेमिक तृतीयक उपयोगकर्ता भूमिकाओं को संभालने के लिए Vue राउटर को रिफैक्टर करें।",
          kn: "ಡೈನಾಮಿಕ್ ತೃತೀಯ ಬಳಕೆದಾರ ಪಾತ್ರಗಳನ್ನು ನಿರ್ವಹಿಸಲು Vue ರೂಟರ್ ಅನ್ನು ರಿಫ್ಯಾಕ್ಟರ್ ಮಾಡಿ.",
        },
        activeLang: "en",
      },
      {
        id: 2,
        title: "Export Monthly Database Backups",
        category: "Maintenance",
        dueDate: "2026-03-05",
        status: "Pending",
        lastUpdated: "Not updated yet",
        description: {
          en: "Run the Celery scheduled job to export the TASKS table.",
        },
        activeLang: "en",
      },
    ];
  }
};
const showPopup = ref(false);
const overdueTasks = computed(() => {
  return tasks.value.filter(
    (tk) => new Date(tk.dueDate) < new Date() && tk.status !== "Completed"
  );
});
const alertsCount = computed(() => overdueTasks.value.length);

const notifications = ref([]);
const unreadNotifications = computed(() =>
  notifications.value.filter((n) => !n.is_read)
);
const loadNotifications = async () => {
  if (USE_REAL_BACKEND) {
    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/notifications/unread",
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer DUMMY_TOKEN",
          },
        }
      );
      if (response.ok) {
        notifications.value = await response.json();
      }
    } catch (error) {
      console.error("Error connecting to Flask:", error);
    }
  } else {
    notifications.value = [
      {
        notification_id: 101,
        type: "System",
        message: "Hello there! Welcome to the new task portal.",
        is_read: false,
        created_at: "Just now",
      },
      {
        notification_id: 102,
        type: "Assignment",
        message:
          "You were assigned a new task: Export Monthly Database Backups",
        is_read: false,
        created_at: "2 hours ago",
      },
    ];
  }
};
const markAsRead = async (notificationId) => {
  const targetNotif = notifications.value.find(
    (n) => n.notification_id === notificationId
  );
  if (targetNotif) targetNotif.is_read = true;

  if (USE_REAL_BACKEND) {
    try {
      const response = await fetch(
        `http://127.0.0.1:5000/api/notifications/${notificationId}/read`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer DUMMY_TOKEN",
          },
          body: JSON.stringify({ is_read: true }),
        }
      );

      if (!response.ok) {
        if (targetNotif) targetNotif.is_read = false;
      }
    } catch (error) {
      if (targetNotif) targetNotif.is_read = false;
    }
  }
};
const terminateAccount = async () => {
  const isConfirmed = confirm(
    "Are you sure you want to terminate your account? You will lose access immediately."
  );
  if (!isConfirmed) return;

  if (USE_REAL_BACKEND) {
    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/users/terminate",
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer DUMMY_TOKEN",
          },
        }
      );
      if (response.ok) {
        alert("Account successfully terminated.");
        router.push("/login");
      }
    } catch (error) {
      console.error("Error terminating account:", error);
    }
  } else {
    alert("DEMO: Account theoretically marked as inactive. Logging you out...");
    router.push("/login");
  }
};
onMounted(() => {
  loadUserProfile();
  loadTasks();
  loadNotifications();
});

const filteredTasks = computed(() => {
  if (currentFilter.value === "All") return tasks.value;
  return tasks.value.filter((task) => task.status === currentFilter.value);
});
const updateStatus = async (task, newStatus) => {
  const oldStatus = task.status;
  task.status = newStatus;
  task.lastUpdated = new Date().toLocaleString();

  if (USE_REAL_BACKEND) {
    try {
      const response = await fetch(
        `http://127.0.0.1:5000/api/tasks/${task.id}/status`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer DUMMY_TOKEN",
          },
          body: JSON.stringify({ status: newStatus }),
        }
      );

      if (!response.ok) {
        task.status = oldStatus;
        alert("Failed to save status to the database. Reverting.");
      }
    } catch (error) {
      task.status = oldStatus;
      alert("Cannot connect to server.");
    }
  }
};
const setLanguage = (task, lang) => {
  task.activeLang = lang;
};
</script>
<template>
  <div class="staff-layout">
    <header class="navbar">
      <div class="brand">
        <div class="user-info">
          <h2>{{ t.hello }} {{ currentUser.name }}!</h2>
          <span class="role-text">{{ t.role }}</span>
        </div>
      </div>

      <div class="center-hub">
        <button class="hub-btn" @click="showPopup = !showPopup">
          <div class="hub-stat">
            <span class="stat-icon alert-icon">⚠️</span>
            <strong>{{ alertsCount }}</strong> {{ t.alerts }}
          </div>
          <div class="hub-divider"></div>
          <div class="hub-stat">
            <span class="stat-icon notif-icon">🔔</span>
            <strong>{{ unreadNotifications.length }}</strong>
            {{ t.notifications }}
          </div>
        </button>

        <div v-if="showPopup" class="hub-popup">
          <div class="popup-section alerts-bg">
            <h4>{{ t.sysAlerts }}</h4>
            <div v-if="alertsCount === 0" class="empty-state">
              {{ t.noOverdue }}
            </div>
            <ul v-else class="popup-list">
              <li v-for="tk in overdueTasks" :key="tk.id" class="alert-item">
                <span class="alert-dot"></span>
                "<strong>{{ tk.title }}</strong
                >" {{ t.overdueAlert }}
              </li>
            </ul>
          </div>

          <div class="popup-section notifs-bg">
            <h4>{{ t.inbox }}</h4>
            <div v-if="unreadNotifications.length === 0" class="empty-state">
              {{ t.caughtUp }}
            </div>
            <ul v-else class="popup-list">
              <li
                v-for="notif in unreadNotifications"
                :key="notif.notification_id"
                class="notif-item"
              >
                <div class="notif-content">
                  <span class="notif-type">{{ notif.type }}</span>
                  <p>{{ notif.message }}</p>
                </div>
                <button
                  class="read-btn"
                  @click="markAsRead(notif.notification_id)"
                >
                  {{ t.markRead }}
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div class="nav-actions-container">
        <div class="nav-buttons">
          <button class="terminate-btn" @click="terminateAccount">
            {{ t.terminate }}
          </button>
          <button class="logout-btn" @click="$router.push('/login')">
            {{ t.logout }}
          </button>
        </div>

        <div class="language-selector-wrapper">
          <label for="ui-lang">🌐 UI Language:</label>
          <select
            id="ui-lang"
            :value="currentUser.language"
            @change="updateUILanguage"
            class="ui-lang-dropdown"
          >
            <option value="en">English</option>
            <option value="hi">हिन्दी (Hindi)</option>
            <option value="kn">ಕನ್ನಡ (Kannada)</option>
          </select>
        </div>
      </div>
    </header>

    <main class="content-container">
      <div class="filter-bar">
        <button
          v-for="filter in filters"
          :key="filter"
          :class="['filter-btn', { active: currentFilter === filter }]"
          @click="currentFilter = filter"
        >
          {{ t.filters[filter] }}
        </button>
      </div>

      <div class="task-grid">
        <div v-for="tk in filteredTasks" :key="tk.id" class="task-card">
          <div class="task-header">
            <span
              :class="[
                'status-badge',
                tk.status.replace(' ', '-').toLowerCase(),
              ]"
            >
              {{ t.filters[tk.status] }}
            </span>
            <span class="category-tag">{{ tk.category }}</span>
          </div>

          <h3 class="task-title">{{ tk.title }}</h3>

          <div class="task-meta">
            <strong>{{ t.due }}:</strong> {{ tk.dueDate }}
            <span
              v-if="
                new Date(tk.dueDate) < new Date() && tk.status !== 'Completed'
              "
              class="overdue-alert"
            >
              {{ t.overdueAlert }}
            </span>
            <p class="timestamp">
              <strong>{{ t.lastUpdated }}:</strong> {{ tk.lastUpdated }}
            </p>
          </div>

          <div class="translation-section">
            <div class="lang-tabs">
              <button
                :class="{ active: tk.activeLang === 'en' }"
                @click="setLanguage(tk, 'en')"
              >
                EN
              </button>
              <button
                :class="{ active: tk.activeLang === 'kn' }"
                @click="setLanguage(tk, 'kn')"
              >
                KN
              </button>
              <button
                :class="{ active: tk.activeLang === 'hi' }"
                @click="setLanguage(tk, 'hi')"
              >
                HI
              </button>
            </div>
            <p class="task-desc">
              {{ tk.description[tk.activeLang] || tk.description["en"] }}
            </p>
            <p v-if="!tk.description[tk.activeLang]" class="fallback-warning">
              *Translation unavailable, showing English.
            </p>
          </div>

          <div class="task-actions">
            <select
              :value="tk.status"
              @change="updateStatus(tk, $event.target.value)"
              class="status-dropdown"
            >
              <option value="Pending">{{ t.markPending }}</option>
              <option value="In Progress">{{ t.markInProgress }}</option>
              <option value="Completed">{{ t.markCompleted }}</option>
            </select>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.staff-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #a8e063 0%, #f0ff00 100%);
  font-family: "Inter", sans-serif;
  color: #111827;
}
.navbar {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
  padding: 1rem 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  z-index: 50;
}
.brand {
  width: 250px;
}
.user-info {
  display: flex;
  flex-direction: column;
}
.user-info h2 {
  margin: 0;
  color: #1f2937;
  font-size: 1.5rem;
}
.role-text {
  font-size: 0.8rem;
  color: #6b7280;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 0.1rem;
}
.nav-actions-container {
  width: 250px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.75rem;
}

.nav-buttons {
  display: flex;
  gap: 1rem;
}

.language-selector-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #4b5563;
  font-weight: 600;
}

.ui-lang-dropdown {
  padding: 0.25rem 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  font-size: 0.8rem;
  cursor: pointer;
}
.center-hub {
  position: relative;
  display: flex;
  justify-content: center;
}
.hub-btn {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 30px;
  padding: 0.5rem 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}
.hub-btn:hover {
  border-color: #667eea;
  transform: translateY(-1px);
}
.hub-stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #4b5563;
}
.hub-divider {
  width: 1px;
  height: 20px;
  background: #e5e7eb;
}
.alert-icon {
  font-size: 1.1rem;
}
.notif-icon {
  font-size: 1.1rem;
}

.hub-popup {
  position: absolute;
  top: 60px;
  left: 50%;
  transform: translateX(-50%);
  width: 380px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
  border: 1px solid #e5e7eb;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.popup-section {
  padding: 1.25rem;
}
.popup-section h4 {
  margin: 0 0 1rem 0;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #4b5563;
  border-bottom: 2px solid rgba(0, 0, 0, 0.05);
  padding-bottom: 0.5rem;
}
.alerts-bg {
  background: #fffcf2;
  border-bottom: 1px solid #e5e7eb;
}
.notifs-bg {
  background: white;
}
.empty-state {
  font-size: 0.9rem;
  color: #9ca3af;
  font-style: italic;
  text-align: center;
  padding: 1rem 0;
}
.popup-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.alert-item {
  font-size: 0.9rem;
  color: #991b1b;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.alert-dot {
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 50%;
  display: inline-block;
}

.notif-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #f3f4f6;
}
.notif-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
  padding-right: 1rem;
}
.notif-type {
  font-size: 0.7rem;
  font-weight: 700;
  color: #667eea;
  text-transform: uppercase;
}
.notif-content p {
  margin: 0;
  font-size: 0.85rem;
  color: #374151;
  line-height: 1.3;
}
.read-btn {
  background: #e0e7ff;
  color: #4338ca;
  border: none;
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}
.read-btn:hover {
  background: #c7d2fe;
}
.logout-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #e5e7eb;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  font-weight: 600;
}
.logout-btn:hover {
  background: #f9fafb;
}
.terminate-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #fee2e2;
  background: #fef2f2;
  color: #dc2626;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 600;
}
.terminate-btn:hover {
  background: #ef4444;
  color: white;
  border-color: #ef4444;
}
.content-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}
.filter-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
}
.filter-btn {
  padding: 0.5rem 1.5rem;
  border: none;
  background: rgba(255, 255, 255, 0.9);
  color: #4b5563;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}
.filter-btn:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-1px);
}
.filter-btn.active {
  background: #667eea;
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.task-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}
.task-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
}
.task-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
}
.task-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}
.category-tag {
  font-size: 0.8rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 700;
}
.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
}
.status-badge.pending {
  background: #fef3c7;
  color: #d97706;
}
.status-badge.in-progress {
  background: #dbeafe;
  color: #2563eb;
}
.status-badge.completed {
  background: #d1fae5;
  color: #059669;
}
.task-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
  color: #111827;
}
.task-meta {
  font-size: 0.9rem;
  color: #4b5563;
  margin-bottom: 1rem;
}
.overdue-alert {
  color: #ef4444;
  font-weight: 700;
  margin-left: 0.5rem;
}
.timestamp {
  margin: 0.25rem 0 0 0;
  font-size: 0.8rem;
  color: #9ca3af;
}
.translation-section {
  background: #f9fafb;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  flex-grow: 1;
}
.lang-tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0.5rem;
  margin-bottom: 0.5rem;
}
.lang-tabs button {
  background: none;
  border: none;
  font-size: 0.8rem;
  font-weight: 700;
  color: #9ca3af;
  cursor: pointer;
}
.lang-tabs button.active {
  color: #667eea;
}
.task-desc {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.5;
  color: #374151;
}
.fallback-warning {
  margin: 0.5rem 0 0 0;
  font-size: 0.75rem;
  color: #d97706;
  font-style: italic;
}
.task-actions {
  margin-top: auto;
}
.status-dropdown {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.95rem;
  cursor: pointer;
  background: white;
}
@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
    padding: 1rem;
    text-align: center;
  }
  .brand,
  .nav-actions-container {
    width: 100%;
    align-items: center;
  }
  .nav-buttons {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }
  .language-selector-wrapper {
    justify-content: center;
    width: 100%;
    margin-top: 0.5rem;
  }
  .hub-popup {
    width: 90vw;
    left: 50%;
    transform: translateX(-50%);
    top: 100%;
    margin-top: 10px;
    z-index: 100;
  }
  .filter-bar {
    flex-wrap: wrap;
    justify-content: center;
  }
  .filter-btn {
    flex: 1 1 40%;
    text-align: center;
  }
}
</style>
