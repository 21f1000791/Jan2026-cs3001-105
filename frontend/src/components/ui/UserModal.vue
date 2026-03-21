<script setup>
import { reactive, watch } from "vue";

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  editingUser: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(["close", "submit"]);

const form = reactive({
  name: "",
  email: "",
  role: "staff",
  password: "",
});

watch(
  () => props.editingUser,
  (user) => {
    if (!user) {
      form.name = "";
      form.email = "";
      form.role = "staff";
      form.password = "";
      return;
    }

    form.name = user.name || "";
    form.email = user.email || "";
    form.role = user.role || "staff";
    form.password = "";
  },
  { immediate: true }
);

const submit = () => {
  const payload = {
    name: form.name,
    email: form.email,
    role: form.role,
  };

  if (form.password) {
    payload.password = form.password;
  }

  emit("submit", payload);
};
</script>

<template>
  <transition name="fade">
    <div v-if="props.open" class="user-modal-overlay" @click.self="emit('close')">
      <div class="user-modal glass-panel">
        <div class="user-modal__header">
          <h2 class="user-modal__title">{{ props.editingUser ? "Edit User" : "Create User" }}</h2>
          <button @click="emit('close')" class="user-modal__close">Close</button>
        </div>

        <form class="user-modal__form" @submit.prevent="submit">
          <input v-model="form.name" required placeholder="Full name" class="user-modal__field" />
          <input v-model="form.email" type="email" required placeholder="Email" class="user-modal__field" />
          <select v-model="form.role" class="user-modal__field">
            <option value="staff">Staff</option>
            <option value="manager">Manager</option>
          </select>
          <input
            v-model="form.password"
            type="password"
            :placeholder="props.editingUser ? 'New password (optional)' : 'Password'"
            :required="!props.editingUser"
            class="user-modal__field"
          />

          <div class="user-modal__actions">
            <button type="button" @click="emit('close')" class="user-modal__button user-modal__button--cancel">Cancel</button>
            <button type="submit" class="user-modal__button user-modal__button--save">Save</button>
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

.user-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.user-modal {
  border-radius: 1rem;
  padding: 1.25rem;
  width: 92%;
  max-width: 36rem;
}

.user-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.user-modal__title {
  margin: 0;
  font-size: 1.125rem;
  line-height: 1.75rem;
  font-weight: 700;
  color: #0f172a;
}

.user-modal__close {
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
}

.user-modal__form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.user-modal__field {
  width: 100%;
  border: none;
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.8);
  color: #0f172a;
  box-sizing: border-box;
}

.user-modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 0.5rem;
}

.user-modal__button {
  border: none;
  border-radius: 0.5rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
}

.user-modal__button--cancel {
  background: #e2e8f0;
  color: #0f172a;
}

.user-modal__button--save {
  background: #4f46e5;
  color: #ffffff;
  font-weight: 600;
}

:global(html.dark) .user-modal__title {
  color: #f1f5f9;
}

:global(html.dark) .user-modal__field {
  background: #334155;
  color: #f1f5f9;
}

:global(html.dark) .user-modal__button--cancel {
  background: #334155;
  color: #f1f5f9;
}
</style>
