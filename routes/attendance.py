from flask import Blueprint,render_template,request,redirect,url_for,flash
from config import get_db_connection,login_required

attendance=Blueprint("attendance",__name__)

@attendance.route("/attendance")
@login_required
def attendance_list():
    search_term=request.args.get("search","")
    employee_id_filter=request.args.get("employee_id","")
    date_filter=request.args.get("date","")
    status_filter=request.args.get("status","")
    conn=get_db_connection()
    cursor=conn.cursor()
    query="""
        select a.id, a.employee_id, e.employee_id as employee_code, e.first_name, e.last_name,
               a.date, a.check_in, a.check_out, a.status, a.created_at
        from attendance a join employees e on a.employee_id = e.id
    """
    params=[]
    where_added=False
    if search_term:
        query += " where (e.employee_id like %s or e.first_name like %s or e.last_name like %s)"
        like_term=f"%{search_term}%"
        params.extend([like_term,like_term,like_term])
        where_added=True
    if employee_id_filter:
        if where_added:
            query += " and a.employee_id=%s"
        else:
            query += " where a.employee_id=%s"
        params.append(employee_id_filter)
        where_added=True
    if date_filter:
        if where_added:
            query += " and a.date=%s"
        else:
            query += " where a.date=%s"
        params.append(date_filter)
        where_added=True
    if status_filter:
        if where_added:
            query += " and a.status=%s"
        else:
            query += " where a.status=%s"
        params.append(status_filter)
        where_added=True
    query += " order by a.date desc, e.first_name, e.last_name"
    cursor.execute(query,params)
    attendance_records=cursor.fetchall()
    cursor.execute("select id, employee_id, first_name, last_name from employees order by first_name, last_name")
    employees=cursor.fetchall()
    cursor.execute("select distinct status from attendance")
    statuses=[row["status"] for row in cursor.fetchall()]
    cursor.execute("select status, count(*) as count from attendance group by status")
    attendance_summary=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("attendance.html",attendance=attendance_records,attendance_detail=None,employees=employees,search_term=search_term or "",employee_id_filter=employee_id_filter,date_filter=date_filter,status_filter=status_filter,statuses=statuses or [],attendance_summary=attendance_summary or [])

@attendance.route("/attendance/add")
@login_required
def attendance_add():
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("select id, employee_id, first_name, last_name from employees order by first_name, last_name")
    employees=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("attendance_form.html",action="/attendance/add",employees=employees,attendance=None)

@attendance.route("/attendance/add",methods=["POST"])
@login_required
def attendance_add_post():
    employee_id=request.form.get("employee_id","").strip()
    date=request.form.get("date","").strip()
    check_in=request.form.get("check_in","").strip()
    check_out=request.form.get("check_out","").strip()
    status=request.form.get("status","").strip()
    validation_errors={}
    if not employee_id:
        validation_errors["employee_id"]="Employee is required."
    if not date:
        validation_errors["date"]="Date is required."
    if not status:
        validation_errors["status"]="Status is required."
    if not validation_errors.get("employee_id") and employee_id and not validation_errors.get("date") and date:
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("select id from attendance where employee_id = %s and date = %s",(employee_id,date))
        duplicate=cursor.fetchone()
        conn.close()
        if duplicate:
            validation_errors["date"]="Attendance already exists for this employee on this date."
    if validation_errors:
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("select id, employee_id, first_name, last_name from employees order by first_name, last_name")
        employees=cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("attendance_form.html",action="/attendance/add",employees=employees,validation_errors=validation_errors,attendance={"employee_id": employee_id,"date": date,"check_in": check_in,"check_out": check_out,"status": status})
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("insert into attendance (employee_id, date, check_in, check_out, status) values (%s, %s, %s, %s, %s)",(employee_id,date,check_in,check_out,status))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Attendance record added successfully.")
    return redirect(url_for("attendance.attendance_list"))

@attendance.route("/attendance/<int:id>")
@login_required
def attendance_details(id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("""
        select a.id, a.date, a.check_in, a.check_out, a.status, e.employee_id as employee_code,
               e.first_name, e.last_name, e.position, d.name as department_name
        from attendance a join employees e on a.employee_id = e.id
        left join departments d on e.department_id=d.id
        where a.id=%s
    """,(id,))
    att=cursor.fetchone()
    cursor.close()
    conn.close()
    if not att:
        flash("Attendance record not found.")
        return redirect(url_for("attendance.attendance_list"))
    return render_template("attendance.html",attendance_detail=att,attendance=[],employees=[],search_term="",employee_id_filter="",date_filter="",status_filter="",statuses=[],attendance_summary=[])

@attendance.route("/attendance/<int:id>/edit")
@login_required
def attendance_edit(id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("select * from attendance where id = %s",(id,))
    attendance_record=cursor.fetchone()
    if not attendance_record:
        cursor.close()
        conn.close()
        flash("Attendance record not found.")
        return redirect(url_for("attendance.attendance_list"))
    cursor.execute("select id, employee_id, first_name, last_name from employees order by first_name, last_name")
    employees=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("attendance_form.html",action=f"/attendance/{id}/edit",employees=employees,attendance=attendance_record)

@attendance.route("/attendance/<int:id>/edit",methods=["POST"])
@login_required
def attendance_edit_post(id):
    employee_id=request.form.get("employee_id","").strip()
    date=request.form.get("date","").strip()
    check_in=request.form.get("check_in","").strip()
    check_out=request.form.get("check_out","").strip()
    status=request.form.get("status","").strip()
    validation_errors={}
    if not employee_id:
        validation_errors["employee_id"]="Employee is required."
    if not date:
        validation_errors["date"]="Date is required."
    if not status:
        validation_errors["status"]="Status is required."
    if not validation_errors.get("employee_id") and employee_id and not validation_errors.get("date") and date:
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("select id from attendance where employee_id = %s and date = %s and id != %s",(employee_id,date,id))
        duplicate=cursor.fetchone()
        conn.close()
        if duplicate:
            validation_errors["date"]="Attendance already exists for this employee on this date."
    if validation_errors:
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("select id, employee_id, first_name, last_name from employees order by first_name, last_name")
        employees=cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("attendance_form.html",action=f"/attendance/{id}/edit",employees=employees,validation_errors=validation_errors,attendance={"employee_id": employee_id,"date": date,"check_in": check_in,"check_out": check_out,"status": status,"id": id})
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("update attendance set employee_id = %s, date = %s, check_in = %s, check_out = %s, status = %s where id = %s",(employee_id,date,check_in,check_out,status,id))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Attendance record updated successfully.")
    return redirect(url_for("attendance.attendance_list"))

@attendance.route("/attendance/<int:id>/delete",methods=["POST"])
@login_required
def attendance_delete(id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("delete from attendance where id = %s",(id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Attendance record deleted successfully.")
    return redirect(url_for("attendance.attendance_list"))
