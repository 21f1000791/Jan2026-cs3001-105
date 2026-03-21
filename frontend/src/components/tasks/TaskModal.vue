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
});

const emit = defineEmits(["close", "submit"]);

const form = reactive({
  title: "",
  assignedTo: "",
  category: "Development",
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
      form.category = "Development";
      form.priority = "Medium";
      form.dueDate = "";
      form.description = { en: "", hi: "", kn: "" };
      return;
    }
    form.title = task.title || "";
    form.assignedTo = task.assignedTo || "";
    form.category = task.category || "Development";
    form.priority = task.priority || "Medium";
    form.dueDate = task.dueDate || "";
    form.description = task.description
      ? { ...task.description }
      : { en: "", hi: "", kn: "" };
  },
  { immediate: true }
);

const submit = () => {
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
    <div v-if="props.open" class="task-modal-overlay" @click.self="emit('close')">
      <div class="task-modal glass-panel">
        <div class="task-modal__header">
          <h2 class="task-modal__title">{{ props.editingTask ? "Edit Task" : "Create Task" }}</h2>
          <button @click="emit('close')" class="task-modal__close">Close</button>
        </div>

        <form class="task-modal__form" @submit.prevent="submit">
          <div class="task-modal__grid">
            <input v-model="form.title" required placeholder="Task title" class="task-modal__field" />
            <select v-model="form.assignedTo" required class="task-modal__field">
              <option disabled value="">Assign to</option>
              <option v-for="user in props.users" :key="user.id" :value="user.id">{{ user.name }}</option>
            </select>
            <input v-model="form.dueDate" type="date" required class="task-modal__field" />
            <select v-model="form.priority" class="task-modal__field">
              <option>Low</option>
              <option>Medium</option>
              <option>High</option>
            </select>
          </div>

          <textarea v-model="form.description.en" rows="2" class="task-modal__field task-modal__textarea" placeholder="Description (English)"></textarea>
          <textarea v-model="form.description.hi" rows="2" class="task-modal__field task-modal__textarea" placeholder="Description (Hindi)"></textarea>
          <textarea v-model="form.description.kn" rows="2" class="task-modal__field task-modal__textarea" placeholder="Description (Kannada)"></textarea>

          <div class="task-modal__actions">
            <button type="button" @click="emit('close')" class="task-modal__button task-modal__button--cancel">Cancel</button>
            <button type="submit" class="task-modal__button task-modal__button--save">Save</button>
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
  border-radius: 1rem;
  padding: 1.25rem;
  width: 92%;
  max-width: 42rem;
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

@media (min-width: 768px) {
  .task-modal__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
