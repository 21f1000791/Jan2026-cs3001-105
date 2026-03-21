<script setup>
import NotificationBell from "../notifications/NotificationBell.vue";

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    default: "",
  },
  notifications: {
    type: Array,
    default: () => [],
  },
  showNotifications: {
    type: Boolean,
    default: true,
  },
  notificationOpen: {
    type: Boolean,
    default: false,
  },
  darkMode: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "toggle-theme",
  "toggle-notifications",
  "mark-notification-read",
  "logout",
]);
</script>

<template>
  <header class="app-navbar glass-panel">
    <div class="app-navbar__heading">
      <h1 class="app-navbar__title">{{ props.title }}</h1>
      <p class="app-navbar__subtitle soft-text">{{ props.subtitle }}</p>
    </div>

    <div class="app-navbar__actions">
      <button
        @click="emit('toggle-theme')"
        class="app-navbar__button app-navbar__button--theme"
      >
        {{ props.darkMode ? "Light" : "Dark" }} Mode
      </button>

      <NotificationBell
        v-if="props.showNotifications"
        :notifications="props.notifications"
        :open="props.notificationOpen"
        @toggle="emit('toggle-notifications')"
        @mark-read="emit('mark-notification-read', $event)"
      />

      <button
        @click="emit('logout')"
        class="app-navbar__button app-navbar__button--logout"
      >
        Logout
      </button>
    </div>
  </header>
</template>

<style scoped>
.app-navbar {
  position: relative;
  z-index: 200;
  border-radius: 1rem;
  padding: 0.75rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  animation: floatIn 350ms ease-out;
}

.app-navbar__title {
  margin: 0;
  font-size: 1.25rem;
  line-height: 1.75rem;
  font-weight: 700;
  color: #0f172a;
}

.app-navbar__subtitle {
  margin: 0;
  margin-top: 0.125rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.app-navbar__actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  align-self: flex-end;
}

.app-navbar__button {
  border: none;
  border-radius: 9999px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
  font-weight: 600;
  cursor: pointer;
  transition: box-shadow 200ms ease, background-color 200ms ease;
}

.app-navbar__button--theme {
  background: rgba(255, 255, 255, 0.8);
  color: #1e293b;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.15);
}

.app-navbar__button--theme:hover {
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.2);
}

.app-navbar__button--logout {
  background: #0f172a;
  color: #ffffff;
}

.app-navbar__button--logout:hover {
  background: #1e293b;
}

:global(html.dark) .app-navbar__title {
  color: #f1f5f9;
}

:global(html.dark) .app-navbar__button--theme {
  background: #334155;
  color: #f1f5f9;
}

@media (min-width: 768px) {
  .app-navbar {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.5rem;
  }

  .app-navbar__actions {
    align-self: auto;
  }

  .app-navbar__title {
    font-size: 1.5rem;
    line-height: 2rem;
  }
}
</style>
