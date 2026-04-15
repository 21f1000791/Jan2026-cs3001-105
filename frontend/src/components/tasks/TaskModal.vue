<script setup>
import { reactive, watch } from "vue";

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  editingTask: {
    type: Object,
    default: null,
  },
  users: {
    type: Array,
    default: () => [],
  },
  categories: {
    type: Array,
    default: () => [],
  },
  saving: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close", "submit"]);

const form = reactive({
  title: "",
  assignedTo: "",
  category: "Maintenance",
  priority: "Medium",
  dueDate: "",
  description: { en: "", hi: "", kn: "" },
});

watch(
  () => props.editingTask,
  (task) => {
    if (!task) {
      form.title = "";
      form.assignedTo = "";
      form.category = props.categories[0] || "Maintenance";
      form.priority = "Medium";
      form.dueDate = "";
      form.description = { en: "", hi: "", kn: "" };
      return;
    }
    form.title = task.title || "";
    form.assignedTo = task.assignedTo || "";
    form.category = task.category || props.categories[0] || "Maintenance";
    form.priority = task.priority || "Medium";
    form.dueDate = task.dueDate || "";
    form.description = task.description
      ? { ...task.description }
      : { en: "", hi: "", kn: "" };
  },
  { immediate: true }
);

watch(
  () => props.categories,
  (nextCategories) => {
    if (!Array.isArray(nextCategories) || nextCategories.length === 0) {
      return;
    }

    if (!nextCategories.includes(form.category)) {
      form.category = nextCategories[0];
    }
  },
  { immediate: true }
);

const submit = () => {
  if (props.saving) {
    return;
  }

  emit("submit", {
    title: form.title,
    assignedTo: form.assignedTo,
    category: form.category,
    priority: form.priority,
    dueDate: form.dueDate,
    description: { ...form.description },
  });
};
</script>

<template>
  <transition name="fade">
    <div v-if="props.open" class="task-modal-overlay" @click.self="!props.saving && emit('close')">
      <div class="task-modal glass-panel">
        <div v-if="props.saving" class="task-modal__blocking-layer" role="status" aria-live="polite">
          <div class="task-modal__blocking-card">
            <div class="task-modal__saving-spinner" />
            <p class="task-modal__saving-title">Saving task and translating content...</p>
            <p class="task-modal__saving-subtitle">Please wait while we generate language entries.</p>
          </div>
        </div>

        <div class="task-modal__header">
          <h2 class="task-modal__title">{{ props.editingTask ? "Edit Task" : "Create Task" }}</h2>
          <button @click="emit('close')" :disabled="props.saving" class="task-modal__close">Close</button>
        </div>

        <form class="task-modal__form" @submit.prevent="submit">
          <div class="task-modal__grid">
            <input v-model="form.title" :disabled="props.saving" required placeholder="Task title" class="task-modal__field" />
            <select v-model="form.assignedTo" :disabled="props.saving" required class="task-modal__field">
              <option disabled value="">Assign to</option>
              <option v-for="user in props.users" :key="user.id" :value="user.id">{{ user.name }}</option>
            </select>
            <select v-model="form.category" :disabled="props.saving" required class="task-modal__field">
              <option disabled value="">Select category</option>
              <option v-for="category in props.categories" :key="category" :value="category">{{ category }}</option>
            </select>
            <input v-model="form.dueDate" :disabled="props.saving" type="date" required class="task-modal__field" />
            <select v-model="form.priority" :disabled="props.saving" class="task-modal__field">
              <option>Low</option>
              <option>Medium</option>
              <option>High</option>
            </select>
          </div>

          <textarea v-model="form.description.en" :disabled="props.saving" rows="2" class="task-modal__field task-modal__textarea" placeholder="Description (English)"></textarea>
          <textarea v-model="form.description.hi" :disabled="props.saving" rows="2" class="task-modal__field task-modal__textarea" placeholder="Description (Hindi)"></textarea>
          <textarea v-model="form.description.kn" :disabled="props.saving" rows="2" class="task-modal__field task-modal__textarea" placeholder="Description (Kannada)"></textarea>

          <div class="task-modal__actions">
            <button type="button" @click="emit('close')" :disabled="props.saving" class="task-modal__button task-modal__button--cancel">Cancel</button>
            <button type="submit" :disabled="props.saving" class="task-modal__button task-modal__button--save">
              {{ props.saving ? "Saving..." : "Save" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.task-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.task-modal {
  position: relative;
  overflow: hidden;
  border-radius: 1rem;
  padding: 1.25rem;
  width: 92%;
  max-width: 42rem;
}

.task-modal__blocking-layer {
  position: absolute;
  inset: 0;
  z-index: 5;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.35);
  backdrop-filter: blur(2px);
}

.task-modal__blocking-card {
  width: min(92%, 24rem);
  border-radius: 0.9rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(16, 185, 129, 0.32);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.15);
}

.task-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.task-modal__title {
  margin: 0;
  font-size: 1.125rem;
  line-height: 1.75rem;
  font-weight: 700;
  color: #0f172a;
}

.task-modal__close {
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
}

.task-modal__form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.task-modal__grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 0.75rem;
}

.task-modal__field {
  border: none;
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.8);
  color: #0f172a;
  box-sizing: border-box;
}

.task-modal__textarea {
  width: 100%;
  resize: vertical;
}

.task-modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 0.5rem;
}

.task-modal__saving-spinner {
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 9999px;
  border: 2px solid rgba(16, 185, 129, 0.25);
  border-top-color: #059669;
  animation: spin 0.8s linear infinite;
  margin-bottom: 0.5rem;
}

.task-modal__saving-title {
  margin: 0;
  font-weight: 600;
  color: #065f46;
}

.task-modal__saving-subtitle {
  margin: 0.25rem 0 0;
  color: #047857;
  font-size: 0.875rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.task-modal__button {
  border: none;
  border-radius: 0.5rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
}

.task-modal__button--cancel {
  background: #e2e8f0;
  color: #0f172a;
}

.task-modal__button--save {
  background: #10b981;
  color: #ffffff;
  font-weight: 600;
}

:global(html.dark) .task-modal__title {
  color: #f1f5f9;
}

:global(html.dark) .task-modal__field {
  background: #334155;
  color: #f1f5f9;
}

:global(html.dark) .task-modal__button--cancel {
  background: #334155;
  color: #f1f5f9;
}

:global(html.dark) .task-modal__saving {
  background: rgba(16, 185, 129, 0.15);
  border-color: rgba(16, 185, 129, 0.4);
}

:global(html.dark) .task-modal__blocking-layer {
  background: rgba(2, 6, 23, 0.5);
}

:global(html.dark) .task-modal__blocking-card {
  background: rgba(15, 23, 42, 0.95);
  border-color: rgba(16, 185, 129, 0.45);
}

:global(html.dark) .task-modal__saving-title {
  color: #6ee7b7;
}

:global(html.dark) .task-modal__saving-subtitle {
  color: #34d399;
}

@media (min-width: 768px) {
  .task-modal__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
