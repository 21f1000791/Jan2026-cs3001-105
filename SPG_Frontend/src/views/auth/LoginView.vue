<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
const router = useRouter();
const email = ref("");
const password = ref("");
const errorMessage = ref("");
const USE_REAL_BACKEND = false;
const handleLogin = async () => {
  errorMessage.value = "";

  if (USE_REAL_BACKEND) {
    try {
      const response = await fetch("http://127.0.0.1:5000/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email.value,
          password: password.value,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem("auth_token", data.token);
        if (data.role === "manager" || data.role === "admin") {
          router.push("/manager/dashboard");
        } else {
          router.push("/staff/tasks");
        }
      } else {
        errorMessage.value = "No match. Invalid email or password.";
      }
    } catch (error) {
      errorMessage.value = "Backend not responsive. Please try again later.";
      console.error("Login fetch error:", error);
    }
  } else {
    if (email.value === "admin@gmail.com" && password.value === "password") {
      localStorage.setItem("auth_token", "DUMMY_MANAGER_TOKEN");
      router.push("/manager/dashboard");
    } else if (password.value === "password") {
      localStorage.setItem("auth_token", "DUMMY_STAFF_TOKEN");
      router.push("/staff/tasks");
    } else {
      errorMessage.value = "No match. (Hint: Use 'password' as the password)";
    }
  }
};
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="header-text">
        <h2>Task Portal</h2>
        <p>Please enter your credentials to Login</p>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label>Email Address</label>
          <input
            v-model="email"
            type="email"
            placeholder="admin@gmail.com"
            required
          />
        </div>

        <div class="input-group">
          <label>Password</label>
          <input
            v-model="password"
            type="password"
            placeholder="••••••••"
            required
          />
        </div>

        <div v-if="errorMessage" class="error-alert">
          {{ errorMessage }}
        </div>

        <button type="submit" class="login-btn">Login to Dashboard</button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #a8e063 0%, #f0ff00 100%);
  font-family: "Inter", sans-serif;
}
.login-card {
  background: rgba(255, 255, 255, 0.97);
  backdrop-filter: blur(12px);
  padding: 3rem;
  border-radius: 16px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.18);
  width: 100%;
  max-width: 420px;
  border: 1px solid rgba(255, 255, 255, 0.4);
}
.header-text {
  text-align: center;
  margin-bottom: 2rem;
}
.header-text h2 {
  margin: 0;
  font-size: 2.2rem;
  font-weight: 700;
  background: -webkit-linear-gradient(#764ba2, #667eea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.header-text p {
  color: #555;
  margin-top: 0.5rem;
  font-size: 0.95rem;
}
.input-group {
  text-align: left;
  margin-bottom: 1.5rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #444;
  font-size: 0.9rem;
}
input {
  width: 100%;
  padding: 0.85rem;
  border: 2px solid #e1e5ee;
  border-radius: 8px;
  box-sizing: border-box;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}
input:focus {
  outline: none;
  border-color: #667eea;
}
.error-alert {
  background-color: #fef2f2;
  color: #dc2626;
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid #fee2e2;
  font-size: 0.85rem;
  font-weight: 600;
  text-align: center;
  margin-bottom: 1rem;
}
.login-btn {
  width: 100%;
  padding: 0.85rem;
  background: linear-gradient(to right, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.05rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  margin-top: 0.5rem;
}
.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(118, 75, 162, 0.35);
}
</style>
