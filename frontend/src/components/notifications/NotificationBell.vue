<script setup>
import { computed } from "vue";

const props = defineProps({
  notifications: {
    type: Array,
    default: () => [],
  },
  open: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["toggle", "mark-read"]);

const unread = computed(() => props.notifications.filter((n) => !n.is_read));
</script>

<template>
  <div class="notification-bell">
    <button
      @click="emit('toggle')"
      class="notification-bell__trigger"
    >
      Notifications
      <span class="notification-bell__count">
        {{ unread.length }}
      </span>
    </button>

    <transition name="fade-slide">
      <div
        v-if="props.open"
        class="notification-bell__dropdown glass-panel"
      >
        <h4 class="notification-bell__title">Inbox</h4>
        <p v-if="unread.length === 0" class="notification-bell__empty soft-text">No unread notifications.</p>
        <ul v-else class="notification-bell__list">
          <li
            v-for="notification in unread"
            :key="notification.notification_id"
            class="notification-bell__item"
          >
            <p class="notification-bell__type">{{ notification.type }}</p>
            <p class="notification-bell__message">{{ notification.message }}</p>
            <button
              @click="emit('mark-read', notification.notification_id)"
              class="notification-bell__mark"
            >
              Mark as read
            </button>
          </li>
        </ul>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.2s ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.notification-bell {
  position: relative;
}

.notification-bell__trigger {
  position: relative;
  border: none;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.8);
  color: #1e293b;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.15);
  transition: box-shadow 200ms ease;
  cursor: pointer;
}

.notification-bell__trigger:hover {
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.2);
}

.notification-bell__count {
  margin-left: 0.5rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.5rem;
  height: 1.5rem;
  border-radius: 9999px;
  background: #f59e0b;
  color: #ffffff;
  font-size: 0.75rem;
  line-height: 1rem;
  padding: 0 0.25rem;
}

.notification-bell__dropdown {
  position: absolute;
  right: 0;
  margin-top: 0.75rem;
  width: 20rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.75rem;
  z-index: 1200;
}

.notification-bell__title {
  margin: 0 0 0.5rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
  font-weight: 600;
  color: #334155;
}

.notification-bell__empty {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.25rem;
  padding: 0.5rem 0;
}

.notification-bell__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 18rem;
  overflow: auto;
}

.notification-bell__item {
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.7);
  padding: 0.5rem;
}

.notification-bell__type {
  margin: 0;
  font-size: 0.75rem;
  line-height: 1rem;
  font-weight: 600;
  color: #4f46e5;
}

.notification-bell__message {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  line-height: 1.25rem;
  color: #334155;
}

.notification-bell__mark {
  margin-top: 0.5rem;
  border: none;
  background: transparent;
  padding: 0;
  font-size: 0.75rem;
  line-height: 1rem;
  font-weight: 500;
  color: #047857;
  cursor: pointer;
}

:global(html.dark) .notification-bell__trigger {
  background: #334155;
  color: #f1f5f9;
}

:global(html.dark) .notification-bell__title {
  color: #f1f5f9;
}

:global(html.dark) .notification-bell__item {
  background: rgba(51, 65, 85, 0.8);
}

:global(html.dark) .notification-bell__type {
  color: #a5b4fc;
}

:global(html.dark) .notification-bell__message {
  color: #e2e8f0;
}

:global(html.dark) .notification-bell__mark {
  color: #6ee7b7;
}
</style>
