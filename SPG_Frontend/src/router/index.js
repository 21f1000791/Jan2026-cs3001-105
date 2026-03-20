import { createRouter, createWebHistory } from "vue-router";
const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: () => import("../views/auth/LoginView.vue") },
  {
    path: "/manager/dashboard",
    component: () => import("../views/manager/ManagerDashboard.vue"),
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
export default router;
