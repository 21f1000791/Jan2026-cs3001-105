<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const USE_REAL_BACKEND = false;
const activeTab = ref("tasks");
const currentUser = ref({ name: "Loading...", role: "" });
const loadUserProfile = async () => {
  if (USE_REAL_BACKEND) {
    try {
      const response = await fetch("http://127.0.0.1:5000/api/users/me", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
        },
      });
      if (response.ok) currentUser.value = await response.json();
    } catch (error) {
      console.error("Fetch error:", error);
    }
  } else {
    currentUser.value = { name: "Admin User", role: "Manager" };
  }
};
//TASK
const tasks = ref([]);
const taskSearchQuery = ref("");
const taskSortOption = ref("dueDateAsc");

const taskCategories = [
  "Development",
  "Maintenance",
  "Testing",
  "Design",
  "Support",
  "Other",
];

const loadTasks = async () => {
  if (USE_REAL_BACKEND) {
    try {
      const response = await fetch("http://127.0.0.1:5000/api/tasks/all", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
        },
      });
      if (response.ok) tasks.value = await response.json();
    } catch (error) {
      console.error("Fetch error:", error);
    }
  } else {
    tasks.value = [
      {
        id: 1,
        title: "Update Frontend Routing",
        assignedTo: "Priyangshu",
        category: "Development",
        priority: "High",
        status: "In Progress",
        dueDate: "2026-03-10",
        description: { en: "Fix the Vue router bugs.", hi: "", kn: "" },
      },
      {
        id: 2,
        title: "Export Monthly Backups",
        assignedTo: "Rahul",
        category: "Maintenance",
        priority: "Medium",
        status: "Pending",
        dueDate: "2026-03-05",
        description: { en: "Run the DB export script.", hi: "", kn: "" },
      },
      {
        id: 3,
        title: "Review Translation API",
        assignedTo: "Priyangshu",
        category: "Testing",
        priority: "Low",
        status: "Completed",
        dueDate: "2026-03-15",
        description: { en: "Check translation endpoints.", hi: "", kn: "" },
      },
      {
        id: 4,
        title: "Fix Login Auth Bug",
        assignedTo: "Anjali",
        category: "Development",
        priority: "High",
        status: "Pending",
        dueDate: "2026-03-01",
        description: { en: "JWT token not saving properly.", hi: "", kn: "" },
      },
    ];
  }
};

const processedTasks = computed(() => {
  let result = tasks.value;
  if (taskSearchQuery.value) {
    const q = taskSearchQuery.value.toLowerCase();
    result = result.filter(
      (t) =>
        t.title.toLowerCase().includes(q) ||
        t.category.toLowerCase().includes(q) ||
        t.assignedTo.toLowerCase().includes(q)
    );
  }
  result = result.sort((a, b) => {
    if (taskSortOption.value === "dueDateAsc")
      return new Date(a.dueDate) - new Date(b.dueDate);
    if (taskSortOption.value === "dueDateDesc")
      return new Date(b.dueDate) - new Date(a.dueDate);
    if (taskSortOption.value === "status")
      return a.status.localeCompare(b.status);
    return 0;
  });
  return result;
});

const deleteTask = async (taskId) => {
  const isConfirmed = confirm(
    "Are you sure you want to delete this task? This action cannot be undone."
  );
  if (!isConfirmed) return;
  if (USE_REAL_BACKEND) {
    try {
      const response = await fetch(
        `http://127.0.0.1:5000/api/tasks/${taskId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
          },
        }
      );
      if (response.ok) {
        tasks.value = tasks.value.filter((t) => t.id !== taskId);
        alert("Task deleted successfully.");
      }
    } catch (error) {
      console.error("Delete error:", error);
    }
  } else {
    tasks.value = tasks.value.filter((t) => t.id !== taskId);
    alert("DEMO: Task deleted.");
  }
};

const showTaskModal = ref(false);
const isEditingTask = ref(false);
const editingTaskId = ref(null);
const formActiveLang = ref("en");

const taskFormTemplate = {
  title: "",
  assignedTo: "",
  category: "Development",
  priority: "Medium",
  dueDate: "",
  description: { en: "", hi: "", kn: "" },
};
const taskFormData = ref(JSON.parse(JSON.stringify(taskFormTemplate)));

const openCreateTaskModal = () => {
  isEditingTask.value = false;
  editingTaskId.value = null;
  taskFormData.value = JSON.parse(JSON.stringify(taskFormTemplate));
  formActiveLang.value = "en";
  showTaskModal.value = true;
};

const openEditTaskModal = (task) => {
  isEditingTask.value = true;
  editingTaskId.value = task.id;
  taskFormData.value = {
    ...task,
    description: task.description
      ? JSON.parse(JSON.stringify(task.description))
      : { en: "", hi: "", kn: "" },
  };
  formActiveLang.value = "en";
  showTaskModal.value = true;
};

const submitTaskForm = async () => {
  if (
    !taskFormData.value.title ||
    !taskFormData.value.assignedTo ||
    !taskFormData.value.dueDate
  )
    return alert("Fill in Title, Assignee, and Due Date.");

  if (USE_REAL_BACKEND) {
    const url = isEditingTask.value
      ? `http://127.0.0.1:5000/api/tasks/${editingTaskId.value}`
      : "http://127.0.0.1:5000/api/tasks";
    const method = isEditingTask.value ? "PUT" : "POST";
    try {
      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
        },
        body: JSON.stringify(taskFormData.value),
      });
      if (response.ok) {
        alert(
          `Task ${isEditingTask.value ? "updated" : "created"} successfully!`
        );
        loadTasks();
        showTaskModal.value = false;
      }
    } catch (error) {
      console.error("Submit error:", error);
    }
  } else {
    if (isEditingTask.value) {
      const idx = tasks.value.findIndex((t) => t.id === editingTaskId.value);
      if (idx !== -1)
        tasks.value[idx] = {
          ...tasks.value[idx],
          ...taskFormData.value,
          lastUpdated: new Date().toLocaleString(),
        };
      alert("DEMO: Task updated!");
    } else {
      tasks.value.unshift({
        id: Math.floor(Math.random() * 100000),
        ...taskFormData.value,
        status: "Pending",
        lastUpdated: new Date().toLocaleString(),
      });
      alert("DEMO: Task created!");
    }
    showTaskModal.value = false;
  }
};
//USER
const users = ref([]);
const userSearchQuery = ref("");

const loadUsers = async () => {
  if (USE_REAL_BACKEND) {
    try {
      const response = await fetch("http://127.0.0.1:5000/api/users", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
        },
      });
      if (response.ok) users.value = await response.json();
    } catch (error) {
      console.error("User fetch error:", error);
    }
  } else {
    users.value = [
      {
        id: 101,
        name: "Priyangshu",
        email: "priyangshu@test.com",
        role: "staff",
        is_active: true,
        tasks_completed: 42,
      },
      {
        id: 102,
        name: "Rahul",
        email: "rahul@test.com",
        role: "staff",
        is_active: true,
        tasks_completed: 18,
      },
      {
        id: 103,
        name: "Anjali",
        email: "anjali@test.com",
        role: "staff",
        is_active: true,
        tasks_completed: 56,
      },
      {
        id: 104,
        name: "Admin User",
        email: "admin@gmail.com",
        role: "manager",
        is_active: true,
        tasks_completed: 0,
      },
      {
        id: 105,
        name: "Vikram",
        email: "vikram@test.com",
        role: "staff",
        is_active: false,
        tasks_completed: 5,
      },
    ];
  }
};

const processedUsers = computed(() => {
  if (!userSearchQuery.value) return users.value;
  const q = userSearchQuery.value.toLowerCase();
  return users.value.filter(
    (u) =>
      u.name.toLowerCase().includes(q) ||
      u.email.toLowerCase().includes(q) ||
      u.role.toLowerCase().includes(q)
  );
});
const activeStaffMembers = computed(() =>
  users.value.filter((u) => u.role === "staff" && u.is_active)
);

const deleteUser = async (userId) => {
  const isConfirmed = confirm(
    "Are you sure you want to terminate this user? They will lose access."
  );
  if (!isConfirmed) return;
  if (USE_REAL_BACKEND) {
    try {
      const response = await fetch(
        `http://127.0.0.1:5000/api/users/${userId}/terminate`,
        {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
          },
        }
      );
      if (response.ok) {
        const u = users.value.find((u) => u.id === userId);
        if (u) u.is_active = false;
        alert("User deactivated successfully.");
      }
    } catch (error) {
      console.error("User delete error:", error);
    }
  } else {
    const u = users.value.find((u) => u.id === userId);
    if (u) u.is_active = false;
    alert("DEMO: User marked as inactive.");
  }
};
const showUserModal = ref(false);
const isEditingUser = ref(false);
const editingUserId = ref(null);

const userFormTemplate = { name: "", email: "", role: "staff", password: "" };
const userFormData = ref({ ...userFormTemplate });

const openCreateUserModal = () => {
  isEditingUser.value = false;
  editingUserId.value = null;
  userFormData.value = { ...userFormTemplate };
  showUserModal.value = true;
};

const openEditUserModal = (user) => {
  isEditingUser.value = true;
  editingUserId.value = user.id;
  userFormData.value = {
    name: user.name,
    email: user.email,
    role: user.role,
    password: "",
  };
  showUserModal.value = true;
};

const submitUserForm = async () => {
  if (!userFormData.value.name || !userFormData.value.email)
    return alert("Name and Email are required.");

  if (USE_REAL_BACKEND) {
    const url = isEditingUser.value
      ? `http://127.0.0.1:5000/api/users/${editingUserId.value}`
      : "http://127.0.0.1:5000/api/users";
    const method = isEditingUser.value ? "PUT" : "POST";
    try {
      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
        },
        body: JSON.stringify(userFormData.value),
      });
      if (response.ok) {
        alert(
          `User ${isEditingUser.value ? "updated" : "created"} successfully!`
        );
        loadUsers();
        showUserModal.value = false;
      }
    } catch (error) {
      console.error("Submit error:", error);
    }
  } else {
    if (isEditingUser.value) {
      const idx = users.value.findIndex((u) => u.id === editingUserId.value);
      if (idx !== -1)
        users.value[idx] = {
          ...users.value[idx],
          name: userFormData.value.name,
          email: userFormData.value.email,
          role: userFormData.value.role,
        };
      alert("DEMO: User updated!");
    } else {
      users.value.unshift({
        id: Math.floor(Math.random() * 1000),
        name: userFormData.value.name,
        email: userFormData.value.email,
        role: userFormData.value.role,
        is_active: true,
        tasks_completed: 0,
      });
      alert("DEMO: User created!");
    }
    showUserModal.value = false;
  }
};
const showHubPopup = ref(false);
const showCreateNotifModal = ref(false);

const overdueTasks = computed(() =>
  tasks.value.filter(
    (t) => new Date(t.dueDate) < new Date() && t.status !== "Completed"
  )
);
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
          headers: {
            Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
          },
        }
      );
      if (response.ok) notifications.value = await response.json();
    } catch (error) {
      console.error("Fetch error:", error);
    }
  } else {
    notifications.value = [
      {
        notification_id: 201,
        type: "System",
        message: "Monthly reports are ready for export.",
        is_read: false,
        created_at: "1 hr ago",
      },
    ];
  }
};
const markAsRead = async (id) => {
  const target = notifications.value.find((n) => n.notification_id === id);
  if (target) target.is_read = true;
  if (USE_REAL_BACKEND) {
    try {
      await fetch(`http://127.0.0.1:5000/api/notifications/${id}/read`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
        },
        body: JSON.stringify({ is_read: true }),
      });
    } catch (error) {
      if (target) target.is_read = false;
    }
  }
};
const notifTemplate = {
  user_id: "All",
  type: "Reminder",
  message: "",
  scheduled_for: "",
};
const newNotif = ref({ ...notifTemplate });
const publishNotification = async () => {
  if (!newNotif.value.message) return alert("Message is required.");
  if (USE_REAL_BACKEND) {
    try {
      const response = await fetch("http://127.0.0.1:5000/api/notifications", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
        },
        body: JSON.stringify(newNotif.value),
      });
      if (response.ok) {
        alert("Notification published successfully!");
        showCreateNotifModal.value = false;
        newNotif.value = { ...notifTemplate };
      }
    } catch (error) {
      console.error("Notif error:", error);
    }
  } else {
    if (
      newNotif.value.user_id === "All" ||
      newNotif.value.user_id === currentUser.value.name
    ) {
      notifications.value.unshift({
        notification_id: Math.floor(Math.random() * 1000),
        type: newNotif.value.type,
        message: newNotif.value.message,
        is_read: false,
        created_at: "Just now",
      });
    }
    alert(`DEMO: Notification published!`);
    showCreateNotifModal.value = false;
    showHubPopup.value = false;
    newNotif.value = { ...notifTemplate };
  }
};
const showStatsModal = ref(false);
const statsTimeframe = ref("Monthly");
const chartActiveMetric = ref("Total");

const currentMetrics = computed(() => {
  const base = {
    total: tasks.value.length,
    completed: tasks.value.filter((t) => t.status === "Completed").length,
    pending: tasks.value.filter((t) => t.status === "Pending").length,
    overdue: overdueTasks.value.length,
  };
  if (statsTimeframe.value === "Daily")
    return { total: 12, completed: 8, pending: 4, overdue: 0 };
  if (statsTimeframe.value === "Weekly")
    return { total: 45, completed: 30, pending: 10, overdue: 5 };
  if (statsTimeframe.value === "All Time")
    return { total: 850, completed: 710, pending: 80, overdue: 60 };
  return base;
});

const completionRate = computed(() =>
  currentMetrics.value.total === 0
    ? 0
    : Math.round(
        (currentMetrics.value.completed / currentMetrics.value.total) * 100
      )
);
const chartData = computed(() => {
  const mockData = {
    Daily: {
      Total: [
        { label: "8 AM", val: 3 },
        { label: "12 PM", val: 5 },
        { label: "4 PM", val: 2 },
        { label: "8 PM", val: 2 },
      ],
      Completed: [
        { label: "8 AM", val: 2 },
        { label: "12 PM", val: 3 },
        { label: "4 PM", val: 2 },
        { label: "8 PM", val: 1 },
      ],
      Pending: [
        { label: "8 AM", val: 1 },
        { label: "12 PM", val: 2 },
        { label: "4 PM", val: 0 },
        { label: "8 PM", val: 1 },
      ],
      Overdue: [
        { label: "8 AM", val: 0 },
        { label: "12 PM", val: 0 },
        { label: "4 PM", val: 0 },
        { label: "8 PM", val: 0 },
      ],
    },
    Weekly: {
      Total: [
        { label: "Mon", val: 12 },
        { label: "Wed", val: 15 },
        { label: "Fri", val: 10 },
        { label: "Sun", val: 8 },
      ],
      Completed: [
        { label: "Mon", val: 8 },
        { label: "Wed", val: 10 },
        { label: "Fri", val: 7 },
        { label: "Sun", val: 5 },
      ],
      Pending: [
        { label: "Mon", val: 3 },
        { label: "Wed", val: 4 },
        { label: "Fri", val: 2 },
        { label: "Sun", val: 1 },
      ],
      Overdue: [
        { label: "Mon", val: 1 },
        { label: "Wed", val: 1 },
        { label: "Fri", val: 1 },
        { label: "Sun", val: 2 },
      ],
    },
    Monthly: {
      Total: [
        { label: "Week 1", val: 35 },
        { label: "Week 2", val: 42 },
        { label: "Week 3", val: 28 },
        { label: "Week 4", val: 19 },
      ],
      Completed: [
        { label: "Week 1", val: 28 },
        { label: "Week 2", val: 32 },
        { label: "Week 3", val: 22 },
        { label: "Week 4", val: 16 },
      ],
      Pending: [
        { label: "Week 1", val: 5 },
        { label: "Week 2", val: 7 },
        { label: "Week 3", val: 5 },
        { label: "Week 4", val: 3 },
      ],
      Overdue: [
        { label: "Week 1", val: 2 },
        { label: "Week 2", val: 3 },
        { label: "Week 3", val: 1 },
        { label: "Week 4", val: 0 },
      ],
    },
    "All Time": {
      Total: [
        { label: "Q1", val: 215 },
        { label: "Q2", val: 238 },
        { label: "Q3", val: 195 },
        { label: "Q4", val: 202 },
      ],
      Completed: [
        { label: "Q1", val: 180 },
        { label: "Q2", val: 195 },
        { label: "Q3", val: 165 },
        { label: "Q4", val: 170 },
      ],
      Pending: [
        { label: "Q1", val: 20 },
        { label: "Q2", val: 25 },
        { label: "Q3", val: 18 },
        { label: "Q4", val: 17 },
      ],
      Overdue: [
        { label: "Q1", val: 15 },
        { label: "Q2", val: 18 },
        { label: "Q3", val: 12 },
        { label: "Q4", val: 15 },
      ],
    },
  };
  const selectedData = mockData[statsTimeframe.value][chartActiveMetric.value];
  const maxVal = Math.max(...selectedData.map((d) => d.val), 1);
  return selectedData.map((d) => ({
    label: d.label,
    val: d.val,
    heightPercentage: (d.val / maxVal) * 100,
  }));
});
const getChartColor = () => {
  if (chartActiveMetric.value === "Completed") return "#10b981";
  if (chartActiveMetric.value === "Pending") return "#f59e0b";
  if (chartActiveMetric.value === "Overdue") return "#ef4444";
  return "#4f46e5";
};

const handleExport = (type) => {
  alert(
    `Triggering ${type} export job. The backend will generate and download the file.`
  );
};
onMounted(() => {
  loadUserProfile();
  loadTasks();
  loadUsers();
  loadNotifications();
});
</script>
<template>
  <div class="manager-layout">
    <header class="navbar">
      <div class="brand">
        <div class="user-info">
          <h2>Manager Portal</h2>
          <span class="role-text">Welcome, {{ currentUser.name }}</span>
        </div>
      </div>

      <div class="center-hub">
        <button class="hub-btn" @click="showHubPopup = !showHubPopup">
          <div class="hub-stat">
            <span class="stat-icon">⚠️</span
            ><strong>{{ overdueTasks.length }}</strong> Alerts
          </div>
          <div class="hub-divider"></div>
          <div class="hub-stat">
            <span class="stat-icon">🔔</span
            ><strong>{{ unreadNotifications.length }}</strong> Inbox
          </div>
        </button>

        <div v-if="showHubPopup" class="hub-popup">
          <div class="popup-section alerts-bg">
            <h4>System Alerts (Overdue)</h4>
            <div v-if="overdueTasks.length === 0" class="empty-state">
              No overdue tasks.
            </div>
            <ul v-else class="popup-list">
              <li v-for="tk in overdueTasks" :key="tk.id" class="alert-item">
                <span class="alert-dot"></span>"<strong>{{ tk.title }}</strong
                >" by {{ tk.assignedTo }} is overdue!
              </li>
            </ul>
          </div>
          <div class="popup-section notifs-bg">
            <div class="notif-header">
              <h4>My Inbox</h4>
              <button
                class="create-notif-link"
                @click="
                  showCreateNotifModal = true;
                  showHubPopup = false;
                "
              >
                + Send Alert
              </button>
            </div>
            <div v-if="unreadNotifications.length === 0" class="empty-state">
              Inbox empty.
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
                  Mark Read
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div class="nav-actions">
        <button class="stats-btn" @click="showStatsModal = true">
          📊 Task Statistics
        </button>
        <button class="export-btn" @click="handleExport('CSV')">
          📄 Export CSV
        </button>
        <button class="logout-btn" @click="$router.push('/login')">
          Logout
        </button>
      </div>
    </header>

    <main class="content-container">
      <div class="view-toggle-container">
        <div class="view-tabs">
          <button
            :class="['tab-btn', { active: activeTab === 'tasks' }]"
            @click="activeTab = 'tasks'"
          >
            Manage Tasks
          </button>
          <button
            :class="['tab-btn', { active: activeTab === 'users' }]"
            @click="activeTab = 'users'"
          >
            Manage Users
          </button>
        </div>
      </div>

      <section v-if="activeTab === 'tasks'" class="task-management">
        <div class="toolbar">
          <div class="search-sort">
            <input
              type="text"
              v-model="taskSearchQuery"
              placeholder="Search tasks, staff, or categories..."
              class="search-input"
            />
            <select v-model="taskSortOption" class="sort-select">
              <option value="dueDateAsc">Sort: Due Date (Earliest)</option>
              <option value="dueDateDesc">Sort: Due Date (Latest)</option>
              <option value="status">Sort: Status</option>
            </select>
          </div>
          <button class="create-btn" @click="openCreateTaskModal">
            + Create New Task
          </button>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Task Title</th>
                <th>Assigned To</th>
                <th>Category</th>
                <th>Priority</th>
                <th>Due Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="task in processedTasks"
                :key="task.id"
                :class="{
                  'overdue-row':
                    new Date(task.dueDate) < new Date() &&
                    task.status !== 'Completed',
                }"
              >
                <td>
                  <strong>{{ task.title }}</strong>
                </td>
                <td>{{ task.assignedTo }}</td>
                <td>
                  <span class="category-tag">{{ task.category }}</span>
                </td>
                <td>
                  <span
                    :class="[
                      'priority-badge',
                      task.priority?.toLowerCase() || 'medium',
                    ]"
                    >{{ task.priority || "Medium" }}</span
                  >
                </td>
                <td>
                  {{ task.dueDate
                  }}<span
                    v-if="
                      new Date(task.dueDate) < new Date() &&
                      task.status !== 'Completed'
                    "
                    class="overdue-icon"
                    >⚠️</span
                  >
                </td>
                <td>
                  <span
                    :class="[
                      'status-badge',
                      task.status.replace(' ', '-').toLowerCase(),
                    ]"
                    >{{ task.status }}</span
                  >
                </td>
                <td class="action-cells">
                  <button
                    class="action-btn edit"
                    @click="openEditTaskModal(task)"
                  >
                    Edit
                  </button>
                  <button
                    class="action-btn delete"
                    @click="deleteTask(task.id)"
                  >
                    Delete
                  </button>
                </td>
              </tr>
              <tr v-if="processedTasks.length === 0">
                <td colspan="7" class="empty-state">No tasks found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-if="activeTab === 'users'" class="user-management">
        <div class="toolbar">
          <div class="search-sort">
            <input
              type="text"
              v-model="userSearchQuery"
              placeholder="Search users by name, email, or role..."
              class="search-input"
            />
          </div>
          <button class="create-btn" @click="openCreateUserModal">
            + Add New User
          </button>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Tasks Completed</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in processedUsers" :key="user.id">
                <td>
                  <strong>{{ user.name }}</strong>
                </td>
                <td>{{ user.email }}</td>
                <td>
                  <span :class="['role-tag', user.role.toLowerCase()]">{{
                    user.role
                  }}</span>
                </td>
                <td>
                  <span
                    :class="[
                      'status-badge',
                      user.is_active ? 'completed' : 'delete',
                    ]"
                  >
                    {{ user.is_active ? "Active" : "Inactive" }}
                  </span>
                </td>
                <td style="font-weight: bold; color: #4f46e5">
                  {{ user.tasks_completed }}
                </td>
                <td class="action-cells">
                  <button
                    class="action-btn edit"
                    @click="openEditUserModal(user)"
                  >
                    Edit
                  </button>
                  <button
                    v-if="user.is_active"
                    class="action-btn delete"
                    @click="deleteUser(user.id)"
                  >
                    Deactivate
                  </button>
                </td>
              </tr>
              <tr v-if="processedUsers.length === 0">
                <td colspan="6" class="empty-state">No users found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>

    <div
      v-if="showTaskModal"
      class="modal-overlay"
      @click.self="showTaskModal = false"
    >
      <div class="stats-modal create-modal">
        <div class="modal-header">
          <h2>{{ isEditingTask ? "Edit Task" : "Create New Task" }}</h2>
          <button class="close-btn" @click="showTaskModal = false">✖</button>
        </div>
        <form @submit.prevent="submitTaskForm" class="create-form">
          <div class="form-row">
            <div class="input-group">
              <label>Task Title *</label
              ><input type="text" v-model="taskFormData.title" required />
            </div>
            <div class="input-group" style="flex: 0.5">
              <label>Category</label
              ><select v-model="taskFormData.category">
                <option v-for="cat in taskCategories" :key="cat" :value="cat">
                  {{ cat }}
                </option>
              </select>
            </div>
            <div class="input-group" style="flex: 0.5">
              <label>Priority</label
              ><select v-model="taskFormData.priority">
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="input-group">
              <label>Assign To *</label>
              <select v-model="taskFormData.assignedTo" required>
                <option value="" disabled>Select staff...</option>
                <option
                  v-for="staff in activeStaffMembers"
                  :key="staff.id"
                  :value="staff.name"
                >
                  {{ staff.name }}
                </option>
              </select>
            </div>
            <div class="input-group">
              <label>Due Date *</label
              ><input type="date" v-model="taskFormData.dueDate" required />
            </div>
          </div>
          <div class="translation-block">
            <label>Task Description & Translations</label>
            <div class="lang-tabs">
              <button
                type="button"
                :class="{ active: formActiveLang === 'en' }"
                @click="formActiveLang = 'en'"
              >
                English
              </button>
              <button
                type="button"
                :class="{ active: formActiveLang === 'hi' }"
                @click="formActiveLang = 'hi'"
              >
                Hindi
              </button>
              <button
                type="button"
                :class="{ active: formActiveLang === 'kn' }"
                @click="formActiveLang = 'kn'"
              >
                Kannada
              </button>
            </div>
            <textarea
              v-model="taskFormData.description[formActiveLang]"
              rows="3"
            ></textarea>
          </div>
          <div class="form-actions">
            <button
              type="button"
              class="cancel-btn"
              @click="showTaskModal = false"
            >
              Cancel
            </button>
            <button type="submit" class="submit-btn">
              {{ isEditingTask ? "Save" : "Assign" }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div
      v-if="showUserModal"
      class="modal-overlay"
      @click.self="showUserModal = false"
    >
      <div class="stats-modal create-modal" style="max-width: 500px">
        <div class="modal-header">
          <h2>{{ isEditingUser ? "Edit User" : "Add New User" }}</h2>
          <button class="close-btn" @click="showUserModal = false">✖</button>
        </div>
        <form @submit.prevent="submitUserForm" class="create-form">
          <div class="input-group" style="margin-bottom: 1rem">
            <label>Full Name *</label
            ><input type="text" v-model="userFormData.name" required />
          </div>
          <div class="input-group" style="margin-bottom: 1rem">
            <label>Email Address *</label
            ><input type="email" v-model="userFormData.email" required />
          </div>
          <div class="form-row">
            <div class="input-group">
              <label>Role</label>
              <select v-model="userFormData.role">
                <option value="staff">Staff Member</option>
                <option value="manager">Manager / Admin</option>
              </select>
            </div>
            <div class="input-group">
              <label
                >Password
                {{
                  isEditingUser ? "(Leave blank to keep current)" : "*"
                }}</label
              >
              <input
                type="password"
                v-model="userFormData.password"
                :required="!isEditingUser"
                placeholder="••••••••"
              />
            </div>
          </div>
          <div class="form-actions">
            <button
              type="button"
              class="cancel-btn"
              @click="showUserModal = false"
            >
              Cancel
            </button>
            <button type="submit" class="submit-btn">
              {{ isEditingUser ? "Save Changes" : "Create User" }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div
      v-if="showCreateNotifModal"
      class="modal-overlay"
      @click.self="showCreateNotifModal = false"
    >
      <div class="stats-modal create-modal" style="max-width: 500px">
        <div class="modal-header">
          <h2>Publish Notification</h2>
          <button class="close-btn" @click="showCreateNotifModal = false">
            ✖
          </button>
        </div>
        <form @submit.prevent="publishNotification" class="create-form">
          <div class="form-row">
            <div class="input-group">
              <label>Target Audience</label>
              <select v-model="newNotif.user_id" required>
                <option value="All">All Active Staff</option>
                <option
                  v-for="staff in activeStaffMembers"
                  :key="staff.id"
                  :value="staff.name"
                >
                  {{ staff.name }}
                </option>
              </select>
            </div>
            <div class="input-group">
              <label>Type</label
              ><select v-model="newNotif.type">
                <option value="Reminder">Reminder</option>
                <option value="Alert">Alert</option>
                <option value="System">System</option>
              </select>
            </div>
          </div>
          <div class="input-group" style="margin-bottom: 1rem">
            <label>Message Content</label
            ><textarea v-model="newNotif.message" rows="3" required></textarea>
          </div>
          <div class="form-actions">
            <button
              type="button"
              class="cancel-btn"
              @click="showCreateNotifModal = false"
            >
              Cancel</button
            ><button
              type="submit"
              class="submit-btn"
              style="background: #4f46e5"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>

    <div
      v-if="showStatsModal"
      class="modal-overlay"
      @click.self="showStatsModal = false"
    >
      <div class="stats-modal">
        <div class="modal-header">
          <h2>Task Analytics Dashboard</h2>
          <button class="close-btn" @click="showStatsModal = false">✖</button>
        </div>
        <div class="timeframe-toggles">
          <button
            v-for="time in ['Daily', 'Weekly', 'Monthly', 'All Time']"
            :key="time"
            :class="['time-btn', { active: statsTimeframe === time }]"
            @click="statsTimeframe = time"
          >
            {{ time }}
          </button>
        </div>
        <section class="metrics-grid">
          <div class="metric-card">
            <h3>Total Tasks</h3>
            <p class="metric-value">{{ currentMetrics.total }}</p>
          </div>
          <div class="metric-card success">
            <h3>Completed</h3>
            <p class="metric-value">{{ currentMetrics.completed }}</p>
            <span class="sub-text">{{ completionRate }}% Completion Rate</span>
          </div>
          <div class="metric-card warning">
            <h3>Pending</h3>
            <p class="metric-value">{{ currentMetrics.pending }}</p>
          </div>
          <div class="metric-card danger">
            <h3>Overdue</h3>
            <p class="metric-value">{{ currentMetrics.overdue }}</p>
          </div>
        </section>
        <div class="chart-container">
          <div class="chart-header">
            <h3>Interactive Plot ({{ statsTimeframe }})</h3>
            <div class="metric-toggles">
              <button
                v-for="metric in ['Total', 'Completed', 'Pending', 'Overdue']"
                :key="metric"
                :class="[
                  'metric-toggle-btn',
                  { active: chartActiveMetric === metric },
                ]"
                @click="chartActiveMetric = metric"
              >
                {{ metric }}
              </button>
            </div>
          </div>
          <div class="css-chart">
            <div
              v-for="(point, index) in chartData"
              :key="index"
              class="chart-bar-wrapper"
            >
              <div class="chart-val-label">{{ point.val }}</div>
              <div
                class="chart-bar"
                :style="{
                  height: point.heightPercentage + '%',
                  backgroundColor: getChartColor(),
                }"
              ></div>
              <div class="chart-x-label">{{ point.label }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.manager-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #f12711 0%, #f5af19 100%);
  font-family: "Inter", sans-serif;
  color: #1f2937;
}
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.95);
  padding: 1rem 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  z-index: 50;
  position: relative;
}
.user-info h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #111827;
}
.role-text {
  font-size: 0.85rem;
  color: #6b7280;
  font-weight: 600;
  text-transform: uppercase;
}
.view-toggle-container {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}
.view-tabs {
  display: flex;
  background: rgba(255, 255, 255, 0.4);
  padding: 0.4rem;
  border-radius: 30px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(5px);
}
.tab-btn {
  background: transparent;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 20px;
  font-weight: 700;
  color: #111827;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}
.tab-btn.active {
  background: white;
  color: #f12711;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
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
.hub-popup {
  position: absolute;
  top: 60px;
  left: 50%;
  transform: translateX(-50%);
  width: 400px;
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
.notif-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid rgba(0, 0, 0, 0.05);
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
}
.notif-header h4 {
  border-bottom: none;
  margin: 0;
  padding: 0;
}
.create-notif-link {
  background: none;
  border: none;
  color: #4f46e5;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
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
  color: #f5af19;
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
}

.nav-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}
.stats-btn {
  padding: 0.5rem 1rem;
  border: none;
  background: #4f46e5;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 700;
  box-shadow: 0 4px 6px rgba(79, 70, 229, 0.2);
}
.export-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  color: #374151;
}
.export-btn.pdf {
  border-color: #fca5a5;
  color: #991b1b;
  background: #fef2f2;
}
.logout-btn {
  padding: 0.5rem 1rem;
  border: none;
  background: #1f2937;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.content-container {
  max-width: 1300px;
  margin: 0 auto;
  padding: 0 2rem 2rem 2rem;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.9);
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}
.search-sort {
  display: flex;
  gap: 1rem;
  flex: 1;
}
.search-input {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  width: 100%;
  max-width: 400px;
}
.sort-select {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
}
.create-btn {
  padding: 0.75rem 1.5rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);
}

.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}
.data-table th,
.data-table td {
  padding: 1.2rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}
.data-table th {
  background: #f9fafb;
  font-size: 0.85rem;
  text-transform: uppercase;
  color: #6b7280;
  letter-spacing: 0.05em;
}
.data-table tr:hover {
  background: #f9fafb;
}
.overdue-row td {
  background: #fef2f2;
}

.category-tag {
  font-size: 0.8rem;
  color: #4b5563;
  font-weight: 600;
  background: #e5e7eb;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
}
.role-tag {
  font-size: 0.75rem;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  font-weight: 700;
  text-transform: uppercase;
  background: #e0e7ff;
  color: #4338ca;
}
.role-tag.manager {
  background: #f3e8ff;
  color: #6d28d9;
}
.overdue-icon {
  margin-left: 0.5rem;
  font-size: 1rem;
}

.priority-badge {
  font-size: 0.75rem;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  font-weight: 700;
  text-transform: uppercase;
  display: inline-block;
}
.priority-badge.high {
  background: #fee2e2;
  color: #dc2626;
}
.priority-badge.medium {
  background: #fef3c7;
  color: #d97706;
}
.priority-badge.low {
  background: #d1fae5;
  color: #059669;
}

.status-badge {
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
  display: inline-block;
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
.status-badge.delete {
  background: #fee2e2;
  color: #dc2626;
}
.action-cells {
  display: flex;
  gap: 0.5rem;
}
.action-btn {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
}
.action-btn.edit {
  background: #e0e7ff;
  color: #4338ca;
}
.action-btn.delete {
  background: #fee2e2;
  color: #dc2626;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
}
.stats-modal {
  background: white;
  width: 90%;
  max-width: 900px;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  max-height: 90vh;
  overflow-y: auto;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #f3f4f6;
  padding-bottom: 1rem;
}
.modal-header h2 {
  margin: 0;
  color: #111827;
}
.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #9ca3af;
  cursor: pointer;
}

.create-modal {
  max-width: 700px;
}
.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}
.input-group {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.input-group label {
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #4b5563;
}
.input-group input,
.input-group select,
textarea {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.95rem;
}
.input-group input:focus,
.input-group select:focus,
textarea:focus {
  outline: none;
  border-color: #f5af19;
  box-shadow: 0 0 0 3px rgba(245, 175, 25, 0.1);
}
.translation-block {
  margin-bottom: 1.5rem;
  background: #f9fafb;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}
.lang-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid #d1d5db;
  padding-bottom: 0.5rem;
}
.lang-tabs button {
  background: none;
  border: none;
  font-size: 0.85rem;
  color: #6b7280;
  cursor: pointer;
  font-weight: 600;
}
.lang-tabs button.active {
  color: #f5af19;
}
textarea {
  width: 100%;
  resize: vertical;
  box-sizing: border-box;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  border-top: 2px solid #f3f4f6;
  padding-top: 1.5rem;
  margin-top: 1rem;
}
.cancel-btn {
  padding: 0.75rem 1.5rem;
  background: #f3f4f6;
  color: #4b5563;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}
.submit-btn {
  padding: 0.75rem 2rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
}
.timeframe-toggles {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
  background: #f3f4f6;
  padding: 0.5rem;
  border-radius: 12px;
  width: fit-content;
  margin-left: auto;
  margin-right: auto;
}
.time-btn {
  border: none;
  background: transparent;
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  color: #6b7280;
  cursor: pointer;
}
.time-btn.active {
  background: white;
  color: #111827;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}
.metric-card {
  background: #f9fafb;
  padding: 1.5rem;
  border-radius: 12px;
  border-top: 4px solid #9ca3af;
  text-align: center;
}
.metric-card.success {
  border-top-color: #10b981;
}
.metric-card.warning {
  border-top-color: #f59e0b;
}
.metric-card.danger {
  border-top-color: #ef4444;
}
.metric-value {
  margin: 0.5rem 0 0 0;
  font-size: 2.2rem;
  font-weight: 800;
  color: #111827;
}
.sub-text {
  font-size: 0.75rem;
  color: #10b981;
  font-weight: 700;
}
.chart-container {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
}
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}
.metric-toggles {
  display: flex;
  gap: 0.5rem;
}
.metric-toggle-btn {
  padding: 0.4rem 0.8rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  color: #4b5563;
}
.metric-toggle-btn.active {
  background: #f5af19;
  color: white;
  border-color: #f5af19;
}
.css-chart {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 250px;
  padding-top: 20px;
  border-bottom: 2px solid #e5e7eb;
  gap: 1rem;
}
.chart-bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
  flex: 1;
  max-width: 60px;
}
.chart-bar {
  width: 100%;
  background: #f5af19;
  border-radius: 4px 4px 0 0;
  transition: height 0.4s ease, background-color 0.3s ease;
  min-height: 5px;
}
@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }
  .nav-actions {
    flex-wrap: wrap;
    justify-content: center;
  }
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  .search-sort {
    flex-direction: column;
  }
  .search-input {
    max-width: 100%;
  }
  .form-row {
    flex-direction: column;
  }
  .hub-popup {
    width: 90vw;
  }
}
</style>
