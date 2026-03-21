<script setup>
const props = defineProps({
  items: {
    type: Array,
    default: () => [],
  },
});
</script>

<template>
  <div class="toast-stack">
    <transition-group name="toast">
      <div
        v-for="toast in props.items"
        :key="toast.id"
        class="toast-stack__item"
        :class="{
          'toast-stack__item--success': toast.type === 'success',
          'toast-stack__item--error': toast.type === 'error',
          'toast-stack__item--info': !toast.type || toast.type === 'info',
        }"
      >
        {{ toast.message }}
      </div>
    </transition-group>
  </div>
</template>

<style scoped>
.toast-stack {
  position: fixed;
  right: 1rem;
  bottom: 1rem;
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.toast-stack__item {
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
  font-weight: 500;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
  color: #ffffff;
}

.toast-stack__item--success {
  background: #059669;
}

.toast-stack__item--error {
  background: #dc2626;
}

.toast-stack__item--info {
  background: #0f172a;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}
.toast-enter-from,
.toast-leave-to {
  transform: translateY(10px);
  opacity: 0;
}
</style>
