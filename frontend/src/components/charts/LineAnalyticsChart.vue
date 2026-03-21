<script setup>
import { computed } from "vue";
import { Line } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
} from "chart.js";

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale
);

const props = defineProps({
  points: {
    type: Array,
    default: () => [],
  },
  label: {
    type: String,
    default: "Tasks",
  },
});

const chartData = computed(() => ({
  labels: props.points.map((p) => p.label),
  datasets: [
    {
      label: props.label,
      data: props.points.map((p) => p.value),
      borderColor: "#667eea",
      backgroundColor: "rgba(102, 126, 234, 0.2)",
      fill: true,
      tension: 0.35,
      pointRadius: 3,
    },
  ],
}));

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: "top",
    },
  },
};
</script>

<template>
  <div class="line-analytics-chart">
    <Line :data="chartData" :options="options" />
  </div>
</template>

<style scoped>
.line-analytics-chart {
  height: 18rem;
  width: 100%;
}
</style>
