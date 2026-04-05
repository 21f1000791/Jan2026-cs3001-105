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
    path: "/admin/dashboard",
    component: () => import("../views/admin/Admin.vue"),
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
  const requiresAdmin = to.path.startsWith("/admin");
  const requiresStaff = to.path.startsWith("/staff");

  if (!token && !isAuthRoute) {
    next("/login");
    return;
  }

  if (token && isAuthRoute) {
    if (role === "admin") {
      next("/admin/dashboard");
      return;
    }
    if (role === "manager") {
      next("/manager/dashboard");
      return;
    }
    if (role === "staff") {
      next("/staff/tasks");
      return;
    }
  }

  if (requiresAdmin && role !== "admin") {
    if (role === "manager") {
      next("/manager/dashboard");
      return;
    }
    next("/staff/tasks");
    return;
  }

  if (requiresManager && role !== "manager") {
    if (role === "admin") {
      next("/admin/dashboard");
      return;
    }
    next("/staff/tasks");
    return;
  }

  if (requiresStaff && (role === "manager" || role === "admin")) {
    if (role === "admin") {
      next("/admin/dashboard");
      return;
    }
    next("/manager/dashboard");
    return;
  }

  next();
});

export default router;
