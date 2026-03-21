<script setup>
const props = defineProps({
  task: {
    type: Object,
    required: true,
  },
  managerView: {
    type: Boolean,
    default: false,
  },
  uiLanguage: {
    type: String,
    default: "en",
  },
});

const emit = defineEmits(["edit", "delete", "status-change", "set-language"]);

const isOverdue = () => {
  return new Date(props.task.dueDate) < new Date() && props.task.status !== "Completed";
};
</script>

<template>
  <article class="task-card glass-panel">
    <div class="task-card__header">
      <h3 class="task-card__title">{{ props.task.title }}</h3>
      <span
        class="task-card__status"
        :class="{
          'task-card__status--pending': props.task.status === 'Pending',
          'task-card__status--progress': props.task.status === 'In Progress',
          'task-card__status--completed': props.task.status === 'Completed',
        }"
      >
        {{ props.task.status }}
      </span>
    </div>

    <p class="task-card__meta soft-text">
      <span class="task-card__meta-label">Category:</span> {{ props.task.category }}
      <span class="task-card__meta-sep">|</span>
      <span class="task-card__meta-label">Due:</span> {{ props.task.dueDate }}
      <span v-if="isOverdue()" class="task-card__overdue">(Overdue)</span>
    </p>

    <p class="task-card__description">
      {{ props.task.description?.[props.uiLanguage] || props.task.description?.en || "No description" }}
    </p>

    <div v-if="!props.managerView" class="task-card__lang-controls">
      <button class="task-card__lang-button" @click="emit('set-language', 'en')">EN</button>
      <button class="task-card__lang-button" @click="emit('set-language', 'hi')">HI</button>
      <button class="task-card__lang-button" @click="emit('set-language', 'kn')">KN</button>
    </div>

    <div class="task-card__footer">
      <template v-if="props.managerView">
        <button @click="emit('edit')" class="task-card__action task-card__action--edit">Edit</button>
        <button @click="emit('delete')" class="task-card__action task-card__action--delete">Delete</button>
      </template>
      <template v-else>
        <select
          :value="props.task.status"
          @change="emit('status-change', $event.target.value)"
          class="task-card__status-select"
        >
          <option value="Pending">Pending</option>
          <option value="In Progress">In Progress</option>
          <option value="Completed">Completed</option>
        </select>
      </template>
    </div>
  </article>
</template>

<style scoped>
.task-card {
  border-radius: 1rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: transform 200ms ease, box-shadow 200ms ease;
  animation: floatIn 350ms ease-out;
}

.task-card:hover {
  transform: translateY(-0.25rem);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
}

.task-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
}

.task-card__title {
  margin: 0;
  font-size: 1.125rem;
  line-height: 1.75rem;
  font-weight: 600;
  color: #0f172a;
}

.task-card__status {
  font-size: 0.75rem;
  line-height: 1rem;
  font-weight: 700;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
}

.task-card__status--pending {
  background: #fef3c7;
  color: #b45309;
}

.task-card__status--progress {
  background: #dbeafe;
  color: #1d4ed8;
}

.task-card__status--completed {
  background: #d1fae5;
  color: #047857;
}

.task-card__meta {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.task-card__meta-label {
  font-weight: 600;
}

.task-card__meta-sep {
  margin: 0 0.25rem;
}

.task-card__overdue {
  margin-left: 0.25rem;
  color: #dc2626;
  font-weight: 600;
}

.task-card__description {
  margin: 0;
  min-height: 2.5rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
  color: #334155;
}

.task-card__lang-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.task-card__lang-button {
  border: none;
  border-radius: 9999px;
  padding: 0.25rem 0.5rem;
  background: #f1f5f9;
  color: #0f172a;
  font-size: 0.75rem;
  line-height: 1rem;
  cursor: pointer;
}

.task-card__footer {
  margin-top: auto;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.task-card__action {
  border: none;
  border-radius: 0.5rem;
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
  font-weight: 600;
  cursor: pointer;
}

.task-card__action--edit {
  background: #e0e7ff;
  color: #4338ca;
}

.task-card__action--delete {
  background: #fee2e2;
  color: #b91c1c;
}

.task-card__status-select {
  border: none;
  border-radius: 0.5rem;
  padding: 0.375rem 0.75rem;
  background: rgba(255, 255, 255, 0.8);
  color: #0f172a;
  font-size: 0.875rem;
  line-height: 1.25rem;
}

:global(html.dark) .task-card__title {
  color: #f1f5f9;
}

:global(html.dark) .task-card__description {
  color: #e2e8f0;
}

:global(html.dark) .task-card__lang-button {
  background: #334155;
  color: #f1f5f9;
}

:global(html.dark) .task-card__status-select {
  background: #334155;
  color: #f1f5f9;
}
</style>
