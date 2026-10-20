from flask import Blueprint,render_template
from config import get_db_connection,login_required

dashboard_bp=Blueprint("dashboard",__name__)

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("select count(*) as count from employees")
    total_employees=cursor.fetchone()["count"]
    cursor.execute("select count(*) as count from departments")
    total_departments=cursor.fetchone()["count"]
    cursor.execute("select count(*) as count from attendance where date = curdate()")
    today_attendance=cursor.fetchone()["count"]
    cursor.execute("select count(*) as count from leaves where status = 'pending'")
    pending_leaves=cursor.fetchone()["count"]

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",total_employees=total_employees,total_departments=total_departments,today_attendance=today_attendance,pending_leaves=pending_leaves
    )
