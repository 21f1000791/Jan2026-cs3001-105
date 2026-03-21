import csv
import io

from fpdf import FPDF
from sqlalchemy import text

from app.models import Task, User


class ExportService:
    @staticmethod
    def export_tasks_csv(tasks):
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["id", "title", "category", "due_date", "priority", "status", "assigned_to", "created_by"])

        for task in tasks:
            writer.writerow(
                [
                    task.id,
                    task.title,
                    task.category,
                    task.due_date.isoformat() if task.due_date else "",
                    task.priority,
                    task.status,
                    task.assigned_to,
                    task.created_by,
                ]
            )

        return buffer.getvalue()

    @staticmethod
    def export_tasks_pdf(tasks):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Community Operations - Tasks Export", ln=True)
        pdf.set_font("Helvetica", size=10)

        for task in tasks:
            line = f"#{task.id} {task.title} | {task.status} | {task.priority}"
            pdf.multi_cell(0, 7, line)

        return bytes(pdf.output(dest="S"))

    @staticmethod
    def export_performance_csv():
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["staff_id", "staff_name", "assigned", "completed"])

        staff_users = User.query.filter(User.role == "staff").all()
        for staff in staff_users:
            assigned = staff.assigned_tasks.filter(text("tasks.is_deleted = 0")).count()
            completed = staff.assigned_tasks.filter(text("tasks.is_deleted = 0"), Task.status == "completed").count()
            writer.writerow([staff.id, staff.name, assigned, completed])

        return buffer.getvalue()
