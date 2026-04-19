<script setup>
import ManagerDashboard from "../manager/ManagerDashboard.vue";
</script>

<template>
  <ManagerDashboard class="admin-override" />
</template>

<style scoped>
/* A flat, professional dark charcoal matte for the Admin portal */
.admin-override {
  background: #1e2022 !important;
  background-image: radial-gradient(circle at center, #2b2e31 0%, #1e2022 100%) !important;
}

/* Ensure Dark Mode blends seamlessly for Admins */
:global(html.dark) .admin-override {
  background: #121212 !important;
  background-image: none !important;
}
</style>