import { apiClient } from "./apiClient";

const defaultManager = {
  metrics: { total: 0, completed: 0, pending: 0, overdue: 0 },
  chartPoints: [],
};

const toMonthLabel = (monthNumber) => {
  const monthIndex = Number(monthNumber) - 1;
  if (Number.isNaN(monthIndex) || monthIndex < 0 || monthIndex > 11) {
    return `M${monthNumber}`;
  }
  return new Date(2026, monthIndex, 1).toLocaleString("en-US", {
    month: "short",
  });
};

export const dashboardService = {
  async getManagerDashboard() {
    const response = await apiClient.get("/dashboard/manager");
    const payload = response.data || {};
    const rawMetrics = payload.metrics || {};

    const total = payload.total_tasks ?? rawMetrics.total_tasks ?? rawMetrics.total ?? 0;
    const completed =
      payload.completed_tasks ?? rawMetrics.completed_tasks ?? rawMetrics.completed ?? 0;
    const pending =
      payload.pending_tasks ?? rawMetrics.pending_tasks ?? rawMetrics.pending ?? 0;
    const overdue = payload.overdue_tasks ?? rawMetrics.overdue_tasks ?? rawMetrics.overdue ?? 0;

    const monthlyStats = payload.monthly_stats || rawMetrics.monthly_stats || [];
    const chartPoints = monthlyStats.map((row) => ({
      label: row.label || toMonthLabel(row.month),
      value: Number(row.value ?? row.count ?? 0),
    }));

    return {
      metrics: {
        total,
        completed,
        pending,
        overdue,
      },
      chartPoints: chartPoints.length ? chartPoints : defaultManager.chartPoints,
    };
  },

  async getStaffDashboard() {
    const response = await apiClient.get("/dashboard/staff");
    const payload = response.data || {};

    return {
      metrics: {
        assigned: payload.assigned_tasks ?? payload.metrics?.assigned ?? 0,
        completed: payload.completed_tasks ?? payload.metrics?.completed ?? 0,
        inProgress: payload.in_progress_tasks ?? payload.metrics?.inProgress ?? 0,
        pending: payload.pending_tasks ?? payload.metrics?.pending ?? 0,
      },
    };
  },
};
