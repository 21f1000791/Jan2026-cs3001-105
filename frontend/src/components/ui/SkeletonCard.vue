<template>
  <div class="skeleton-card glass-panel">
    <div class="skeleton-row skeleton-row--title"></div>
    <div class="skeleton-row skeleton-row--half"></div>
    <div class="skeleton-row skeleton-row--full"></div>
    <div class="skeleton-row skeleton-row--wide"></div>
  </div>
</template>

<style scoped>
.skeleton-card {
  border-radius: 1rem;
  padding: 1rem;
  animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.skeleton-row {
  height: 1rem;
  border-radius: 0.25rem;
  background: rgba(226, 232, 240, 0.7);
}

.skeleton-row + .skeleton-row {
  margin-top: 0.5rem;
}

.skeleton-row--title {
  height: 1.25rem;
  width: 66.666667%;
}

.skeleton-row--half {
  width: 50%;
  margin-top: 0.75rem;
}

.skeleton-row--full {
  width: 100%;
}

.skeleton-row--wide {
  width: 80%;
}

:global(html.dark) .skeleton-row {
  background: rgba(71, 85, 105, 0.7);
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.5;
  }
}
</style>
