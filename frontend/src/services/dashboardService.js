import { apiClient } from "./apiClient";

const defaultManager = {
  metrics: { total: 0, completed: 0, pending: 0, overdue: 0 },
  chartPoints: [],
  analytics: {
    monthlyCreated: [],
    monthlyCompleted: [],
    statusBreakdown: [],
    priorityBreakdown: [],
    categoryBreakdown: [],
    staffPerformance: [],
    usersByRole: { admin: 0, manager: 0, staff: 0 },
    notifications: { total: 0, unread: 0 },
    translationCoverage: {
      multilingualTasks: 0,
      expectedRows: 0,
      actualRows: 0,
      coveragePct: 0,
    },
    overdueRate: 0,
    dueSoonTasks: 0,
  },
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

    const mapSeries = (rows = []) =>
      (rows || []).map((row) => ({
        label: row.label || toMonthLabel(row.month),
        value: Number(row.value ?? row.count ?? 0),
      }));

    const mapBreakdown = (rows = []) =>
      (rows || []).map((row) => ({
        label: row.label || "Unknown",
        value: Number(row.value ?? row.count ?? 0),
      }));

    const usersByRole = payload.active_users_by_role || rawMetrics.active_users_by_role || {};
    const notifications = payload.notifications || rawMetrics.notifications || {};
    const translationCoverage = payload.translation_coverage || rawMetrics.translation_coverage || {};

    return {
      metrics: {
        total,
        completed,
        pending,
        overdue,
      },
      chartPoints: chartPoints.length ? chartPoints : defaultManager.chartPoints,
      analytics: {
        monthlyCreated: mapSeries(payload.monthly_created || rawMetrics.monthly_created),
        monthlyCompleted: mapSeries(payload.monthly_completed || rawMetrics.monthly_completed),
        statusBreakdown: mapBreakdown(payload.status_breakdown || rawMetrics.status_breakdown),
        priorityBreakdown: mapBreakdown(payload.priority_breakdown || rawMetrics.priority_breakdown),
        categoryBreakdown: mapBreakdown(payload.category_breakdown || rawMetrics.category_breakdown),
        staffPerformance: payload.staff_performance || rawMetrics.staff_performance || [],
        usersByRole: {
          admin: Number(usersByRole.admin || 0),
          manager: Number(usersByRole.manager || 0),
          staff: Number(usersByRole.staff || 0),
        },
        notifications: {
          total: Number(notifications.total || 0),
          unread: Number(notifications.unread || 0),
        },
        translationCoverage: {
          multilingualTasks: Number(
            translationCoverage.multilingual_tasks || translationCoverage.multilingualTasks || 0
          ),
          expectedRows: Number(
            translationCoverage.expected_rows || translationCoverage.expectedRows || 0
          ),
          actualRows: Number(
            translationCoverage.actual_rows || translationCoverage.actualRows || 0
          ),
          coveragePct: Number(
            translationCoverage.coverage_pct || translationCoverage.coveragePct || 0
          ),
        },
        overdueRate: Number(payload.overdue_rate || rawMetrics.overdue_rate || 0),
        dueSoonTasks: Number(payload.due_soon_tasks || rawMetrics.due_soon_tasks || 0),
      },
    };
  },

  async getStaffDashboard() {
    const response = await apiClient.get("/dashboard/staff");
    const payload = response.data || {};
    const rawMetrics = payload.metrics || {};

    return {
      metrics: {
        assigned: Number(
          payload.total_assigned ?? rawMetrics.total_assigned ?? rawMetrics.assigned ?? 0
        ),
        completed: Number(
          payload.completed_tasks ?? rawMetrics.completed ?? rawMetrics.completed_tasks ?? 0
        ),
        pending: Number(
          payload.pending_tasks ?? rawMetrics.pending_tasks ?? rawMetrics.pending ?? 0
        ),
        overdue: Number(
          payload.overdue_tasks ?? rawMetrics.overdue_tasks ?? rawMetrics.overdue ?? 0
        ),
        completionRate: Number(
          payload.completion_rate ?? rawMetrics.completion_rate ?? rawMetrics.completionRate ?? 0
        ),
      },
    };
  },
};
