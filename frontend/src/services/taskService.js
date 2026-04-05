import { apiClient } from "./apiClient";

const API_TO_UI_STATUS = {
  todo: "Pending",
  in_progress: "In Progress",
  completed: "Completed",
  overdue: "Overdue",
  blocked: "Blocked",
};

const UI_TO_API_STATUS = {
  Pending: "todo",
  "In Progress": "in_progress",
  Completed: "completed",
  Overdue: "overdue",
  Blocked: "blocked",
  todo: "todo",
  in_progress: "in_progress",
  completed: "completed",
  overdue: "overdue",
  blocked: "blocked",
};

const toDescriptionMap = (description) => {
  if (!description) {
    return { en: "", hi: "", kn: "" };
  }
  if (typeof description === "string") {
    return { en: description, hi: "", kn: "" };
  }
  return {
    en: description.en || description.english || "",
    hi: description.hi || description.hindi || "",
    kn: description.kn || description.kannada || "",
  };
};

const normalizeTask = (task = {}) => ({
  id: task.id,
  title: task.translated_title || task.title || "Untitled",
  assignedTo:
    task.assignedTo ||
    task.assigned_to_name ||
    task.assigned_user?.name ||
    task.assigned_to ||
    "Unassigned",
  category: task.translated_category || task.category || "Maintenance",
  priority: task.priority || "Medium",
  status: API_TO_UI_STATUS[task.status] || task.status || "Pending",
  dueDate: task.dueDate || task.due_date || "",
  description: toDescriptionMap(task.description || task.translations),
  createdBy: task.created_by,
});

const apiPayloadFromTask = (payload = {}) => ({
  title: payload.title,
  category: payload.category,
  priority: payload.priority,
  due_date: payload.dueDate,
  assigned_to:
    payload.assignedTo === "" || payload.assignedTo == null
      ? null
      : Number.isNaN(Number(payload.assignedTo))
        ? payload.assignedTo
        : Number(payload.assignedTo),
  description: payload.description,
  status: UI_TO_API_STATUS[payload.status] || payload.status,
});

export const taskService = {
  async getCategoryCatalog() {
    const response = await apiClient.get("/users/categories");
    return {
      allCategories: response.data?.all_categories || [],
      allowedCategories: response.data?.allowed_categories || [],
    };
  },

  async getAll() {
    const response = await apiClient.get("/tasks");
    const tasks = response.data?.items || response.data || [];
    return tasks.map(normalizeTask);
  },

  async getAssigned(language = "en") {
    const response = await apiClient.get("/tasks/assigned", {
      params: { lang: language },
    });
    const tasks = response.data?.items || response.data || [];
    return tasks.map(normalizeTask);
  },

  async create(payload) {
    const response = await apiClient.post("/tasks", apiPayloadFromTask(payload));
    return normalizeTask(response.data?.task || response.data || payload);
  },

  async update(taskId, payload) {
    const response = await apiClient.put(
      `/tasks/${taskId}`,
      apiPayloadFromTask(payload)
    );
    return normalizeTask(response.data?.task || response.data || { id: taskId, ...payload });
  },

  async updateStatus(taskId, status) {
    const response = await apiClient.patch(`/tasks/${taskId}/status`, {
      status: UI_TO_API_STATUS[status] || status,
    });
    return normalizeTask(response.data?.task || response.data || { id: taskId, status });
  },

  async remove(taskId) {
    await apiClient.delete(`/tasks/${taskId}`);
  },

  async removeHard(taskId) {
    await apiClient.delete(`/tasks/${taskId}/hard`);
  },
};
