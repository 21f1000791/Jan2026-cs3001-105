<script setup>
const props = defineProps({
  items: {
    type: Array,
    default: () => [],
  },
  modelValue: {
    type: String,
    default: "",
  },
  label: {
    type: String,
    default: "Workspace",
  },
});

const emit = defineEmits(["update:modelValue", "navigate"]);

const onClickItem = (item) => {
  emit("update:modelValue", item.key);
  if (item.route) {
    emit("navigate", item.route);
  }
};
</script>

<template>
  <aside class="app-sidebar glass-panel">
    <p class="app-sidebar__label">
      {{ props.label }}
    </p>
    <nav class="app-sidebar__nav">
      <button
        v-for="item in props.items"
        :key="item.key"
        @click="onClickItem(item)"
        class="app-sidebar__item"
        :class="props.modelValue === item.key
          ? 'app-sidebar__item--active'
          : 'app-sidebar__item--idle'"
      >
        <span class="app-sidebar__item-label">{{ item.label }}</span>
      </button>
    </nav>
  </aside>
</template>

<style scoped>
.app-sidebar {
  border-radius: 1rem;
  padding: 0.75rem;
  width: 100%;
  flex-shrink: 0;
  animation: floatIn 350ms ease-out;
}

.app-sidebar__label {
  margin: 0;
  padding: 0.5rem 0.75rem;
  font-size: 0.75rem;
  line-height: 1rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.app-sidebar__nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.app-sidebar__item {
  width: 100%;
  text-align: left;
  padding: 0.625rem 0.75rem;
  border-radius: 0.75rem;
  border: none;
  background: transparent;
  transition: all 200ms ease;
  cursor: pointer;
}

.app-sidebar__item-label {
  font-weight: 500;
}

.app-sidebar__item--active {
  background: rgba(255, 255, 255, 0.9);
  color: #0f172a;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.15);
}

.app-sidebar__item--idle {
  color: #334155;
}

.app-sidebar__item--idle:hover {
  background: rgba(255, 255, 255, 0.7);
}

:global(html.dark) .app-sidebar__label {
  color: #cbd5e1;
}

:global(html.dark) .app-sidebar__item--active {
  background: #334155;
  color: #f1f5f9;
}

:global(html.dark) .app-sidebar__item--idle {
  color: #e2e8f0;
}

:global(html.dark) .app-sidebar__item--idle:hover {
  background: rgba(51, 65, 85, 0.8);
}

@media (min-width: 768px) {
  .app-sidebar {
    width: 16rem;
  }
}
</style>
