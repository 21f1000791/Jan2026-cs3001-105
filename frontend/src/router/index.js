import { createRouter, createWebHistory } from "vue-router";
const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: () => import("../views/auth/LoginView.vue") },
  {
    path: "/register",
    component: () => import("../views/auth/LoginView.vue"),
  },
  {
    path: "/manager/dashboard",
    component: () => import("../views/manager/ManagerDashboard.vue"),
  },
  {
    path: "/manager/analytics",
    component: () => import("../views/manager/AnalyticsView.vue"),
  },
  {
    path: "/staff/tasks",
    component: () => import("../views/staff/StaffTasks.vue"),
  },
];
const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("auth_token");
  const role = (localStorage.getItem("user_role") || "").toLowerCase();
  const isAuthRoute = to.path === "/login" || to.path === "/register";
  const requiresManager = to.path.startsWith("/manager");
  const requiresStaff = to.path.startsWith("/staff");

  if (!token && !isAuthRoute) {
    next("/login");
    return;
  }

  if (token && isAuthRoute) {
    if (role === "manager" || role === "admin") {
      next("/manager/dashboard");
      return;
    }
    if (role === "staff") {
      next("/staff/tasks");
      return;
    }
  }

  if (requiresManager && !(role === "manager" || role === "admin")) {
    next("/staff/tasks");
    return;
  }

  if (requiresStaff && (role === "manager" || role === "admin")) {
    next("/manager/dashboard");
    return;
  }

  next();
});

export default router;
