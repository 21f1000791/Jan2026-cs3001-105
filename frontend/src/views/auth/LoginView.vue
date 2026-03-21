<script setup>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { authService } from "../../services/authService";

const router = useRouter();
const fullName = ref("");
const email = ref("");
const password = ref("");
const role = ref("staff");
const errorMessage = ref("");
const loading = ref(false);
const isRegisterMode = computed(() => router.currentRoute.value.path === "/register");

const submit = async () => {
  errorMessage.value = "";
  loading.value = true;

  try {
    if (isRegisterMode.value) {
      await authService.register({
        email: email.value,
        password: password.value,
        role: role.value,
        name: fullName.value.trim(),
      });
      router.push("/login");
      return;
    }

    const data = await authService.login({ email: email.value, password: password.value });
    localStorage.setItem("auth_token", data.token);
    localStorage.setItem("user_role", data.role || "staff");
    if (data.role === "manager" || data.role === "admin") {
      router.push("/manager/dashboard");
    } else {
      router.push("/staff/tasks");
    }
  } catch (error) {
    errorMessage.value = isRegisterMode.value
      ? "Registration failed. Try a different email."
      : "Invalid credentials. Hint: use password as demo password.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="login-page">
    <div class="login-shell">
      <section class="login-hero">
        <div>
          <p class="login-hero__eyebrow">Community Operations Platform</p>
          <h1 class="login-hero__title">Operations made clear for teams of 10 to 50.</h1>
          <p class="login-hero__description">Track tasks, translations, analytics, and team notifications from one modern workspace.</p>
        </div>
        <ul class="login-hero__list">
          <li>Manager dashboards and exports</li>
          <li>Staff translation-ready task cards</li>
          <li>Role-aware notifications</li>
        </ul>
      </section>

      <section class="login-panel glass-panel">
        <div class="login-panel__header">
          <h2 class="login-panel__title">
            {{ isRegisterMode ? "Create Account" : "Welcome Back" }}
          </h2>
          <button
            @click="router.push(isRegisterMode ? '/login' : '/register')"
            class="login-panel__switch"
          >
            {{ isRegisterMode ? "Login" : "Register" }}
          </button>
        </div>

        <form class="login-form" @submit.prevent="submit">
          <div v-if="isRegisterMode">
            <label class="login-form__label">Full Name</label>
            <input
              v-model="fullName"
              type="text"
              placeholder="e.g. Soham Ghosh"
              required
              class="login-form__field"
            />
          </div>

          <div>
            <label class="login-form__label">Email</label>
            <input
              v-model="email"
              type="email"
              placeholder="admin@gmail.com"
              required
              class="login-form__field"
            />
          </div>

          <div>
            <label class="login-form__label">Password</label>
            <input
              v-model="password"
              type="password"
              placeholder="password"
              required
              class="login-form__field"
            />
          </div>

          <div v-if="isRegisterMode">
            <label class="login-form__label">Account Role</label>
            <select
              v-model="role"
              class="login-form__field"
            >
              <option value="staff">Staff</option>
              <option value="manager">Manager</option>
            </select>
          </div>

          <p v-if="errorMessage" class="login-form__error">
            {{ errorMessage }}
          </p>

          <button
            type="submit"
            :disabled="loading"
            class="login-form__submit"
          >
            {{ loading ? "Please wait..." : isRegisterMode ? "Create Account" : "Login" }}
          </button>
        </form>

        <p class="login-panel__hint">Demo manager login: admin@gmail.com / password</p>
      </section>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #a8e063 0%, #f0ff00 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.login-shell {
  width: 100%;
  max-width: 56rem;
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  border-radius: 1.5rem;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
  animation: floatIn 350ms ease-out;
}

.login-hero {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  padding: 2rem;
  background: linear-gradient(145deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
}

.login-hero__eyebrow {
  margin: 0;
  font-size: 0.75rem;
  line-height: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  opacity: 0.8;
}

.login-hero__title {
  margin: 1rem 0 0;
  font-size: 1.875rem;
  line-height: 2.25rem;
  font-weight: 700;
}

.login-hero__description {
  margin: 1rem 0 0;
  font-size: 0.875rem;
  line-height: 1.25rem;
  opacity: 0.9;
}

.login-hero__list {
  margin: 0;
  padding-left: 1.125rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
  opacity: 0.9;
}

.login-panel {
  padding: 1.5rem;
}

.login-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.login-panel__title {
  margin: 0;
  font-size: 1.5rem;
  line-height: 2rem;
  font-weight: 700;
  color: #0f172a;
}

.login-panel__switch {
  border: none;
  background: transparent;
  color: #4338ca;
  font-size: 0.875rem;
  line-height: 1.25rem;
  font-weight: 600;
  cursor: pointer;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.login-form__label {
  display: block;
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
  font-weight: 600;
  color: #334155;
}

.login-form__field {
  width: 100%;
  box-sizing: border-box;
  border: none;
  border-radius: 0.75rem;
  padding: 0.625rem 1rem;
  background: rgba(255, 255, 255, 0.8);
  color: #0f172a;
}

.login-form__error {
  margin: 0;
  border-radius: 0.5rem;
  background: #fee2e2;
  color: #b91c1c;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
  font-weight: 500;
}

.login-form__submit {
  width: 100%;
  border: none;
  border-radius: 0.75rem;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  font-weight: 600;
  padding: 0.625rem 1rem;
  cursor: pointer;
}

.login-form__submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-panel__hint {
  margin: 1rem 0 0;
  font-size: 0.75rem;
  line-height: 1rem;
  color: #64748b;
}

:global(html.dark) .login-panel__title {
  color: #f1f5f9;
}

:global(html.dark) .login-form__label {
  color: #e2e8f0;
}

:global(html.dark) .login-form__field {
  background: #334155;
  color: #f1f5f9;
}

@media (min-width: 768px) {
  .login-shell {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .login-hero {
    display: flex;
  }

  .login-panel {
    padding: 2rem;
  }
}
</style>
