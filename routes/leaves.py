from flask import Blueprint,render_template,request,redirect,url_for,flash
from config import get_db_connection,login_required

leaves=Blueprint("leaves",__name__)

@leaves.route("/leaves")
@login_required
def leaves_list():
    search_term=request.args.get("search","")
    employee_id_filter=request.args.get("employee_id","")
    leave_type_filter=request.args.get("leave_type","")
    status_filter=request.args.get("status","")
    start_date_filter=request.args.get("start_date","")
    conn=get_db_connection()
    cursor=conn.cursor()
    query="""
        select l.id, l.employee_id, e.employee_id as employee_code, e.first_name, e.last_name,
               l.leave_type, l.start_date, l.end_date, l.reason, l.status, l.created_at
        from leaves l join employees e on l.employee_id = e.id
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
            query += " and l.employee_id=%s"
        else:
            query += " where l.employee_id=%s"
        params.append(employee_id_filter)
        where_added=True
    if leave_type_filter:
        if where_added:
            query += " and l.leave_type=%s"
        else:
            query += " where l.leave_type=%s"
        params.append(leave_type_filter)
        where_added=True
    if status_filter:
        if where_added:
            query += " and l.status=%s"
        else:
            query += " where l.status=%s"
        params.append(status_filter)
        where_added=True
    if start_date_filter:
        if where_added:
            query += " and l.start_date=%s"
        else:
            query += " where l.start_date=%s"
        params.append(start_date_filter)
        where_added=True
    query += " order by l.created_at desc"
    cursor.execute(query,params)
    leaves_records=cursor.fetchall()
    cursor.execute("select id, employee_id, first_name, last_name from employees order by first_name, last_name")
    employees=cursor.fetchall()
    cursor.execute("select distinct leave_type from leaves")
    leave_types=[row["leave_type"] for row in cursor.fetchall()]
    cursor.execute("select distinct status from leaves")
    statuses=[row["status"] for row in cursor.fetchall()]
    cursor.execute("select status, count(*) as count from leaves group by status")
    leave_summary=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("leaves.html",leaves=leaves_records,employees=employees,search_term=search_term or "",employee_id_filter=employee_id_filter,leave_type_filter=leave_type_filter or "",status_filter=status_filter or "",start_date_filter=start_date_filter or "",leave_types=leave_types or [],statuses=statuses or [],leave_summary=leave_summary or [])

@leaves.route("/leaves/add")
@login_required
def leaves_add():
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("select id, employee_id, first_name, last_name from employees order by first_name, last_name")
    employees=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("leave_form.html",action="/leaves/add",employees=employees,leave=None)

@leaves.route("/leaves/add",methods=["POST"])
@login_required
def leaves_add_post():
    employee_id=request.form.get("employee_id","").strip()
    leave_type=request.form.get("leave_type","").strip()
    start_date=request.form.get("start_date","").strip()
    end_date=request.form.get("end_date","").strip()
    reason=request.form.get("reason","").strip()
    status=request.form.get("status","").strip() or "pending"
    validation_errors={}
    if not employee_id:
        validation_errors["employee_id"]="Employee is required."
    if not leave_type:
        validation_errors["leave_type"]="Leave type is required."
    if not start_date:
        validation_errors["start_date"]="Start date is required."
    if not end_date:
        validation_errors["end_date"]="End date is required."
    if validation_errors:
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("select id, employee_id, first_name, last_name from employees order by first_name, last_name")
        employees=cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("leave_form.html",action="/leaves/add",employees=employees,validation_errors=validation_errors,leave={"employee_id": employee_id,"leave_type": leave_type,"start_date": start_date,"end_date": end_date,"reason": reason,"status": status})
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("insert into leaves (employee_id, leave_type, start_date, end_date, reason, status) values (%s, %s, %s, %s, %s, %s)",(employee_id,leave_type,start_date,end_date,reason,status))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Leave added successfully.")
    return redirect(url_for("leaves.leaves_list"))

@leaves.route("/leaves/<int:id>")
@login_required
def leaves_details(id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("""
        select l.id, l.employee_id, e.employee_id as employee_code, e.first_name, e.last_name,
               l.leave_type, l.start_date, l.end_date, l.reason, l.status, l.created_at
        from leaves l join employees e on l.employee_id = e.id
        where l.id=%s
    """,(id,))
    leave=cursor.fetchone()
    cursor.close()
    conn.close()
    if not leave:
        flash("Leave record not found.")
        return redirect(url_for("leaves.leaves_list"))
    return render_template("leaves.html",leave=leave,leaves=[],employees=[],search_term="",employee_id_filter="",leave_type_filter="",status_filter="",start_date_filter="",leave_types=[],statuses=[],leave_summary=[])

@leaves.route("/leaves/<int:id>/edit")
@login_required
def leaves_edit(id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("select * from leaves where id = %s",(id,))
    leave=cursor.fetchone()
    if not leave:
        cursor.close()
        conn.close()
        flash("Leave record not found.")
        return redirect(url_for("leaves.leaves_list"))
    cursor.execute("select id, employee_id, first_name, last_name from employees order by first_name, last_name")
    employees=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("leave_form.html",action=f"/leaves/{id}/edit",employees=employees,leave=leave)

@leaves.route("/leaves/<int:id>/edit",methods=["POST"])
@login_required
def leaves_edit_post(id):
    employee_id=request.form.get("employee_id","").strip()
    leave_type=request.form.get("leave_type","").strip()
    start_date=request.form.get("start_date","").strip()
    end_date=request.form.get("end_date","").strip()
    reason=request.form.get("reason","").strip()
    status=request.form.get("status","").strip()
    validation_errors={}
    if not employee_id:
        validation_errors["employee_id"]="Employee is required."
    if not leave_type:
        validation_errors["leave_type"]="Leave type is required."
    if not start_date:
        validation_errors["start_date"]="Start date is required."
    if not end_date:
        validation_errors["end_date"]="End date is required."
    if validation_errors:
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("select id, employee_id, first_name, last_name from employees order by first_name, last_name")
        employees=cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("leave_form.html",action=f"/leaves/{id}/edit",employees=employees,validation_errors=validation_errors,leave={"employee_id": employee_id,"leave_type": leave_type,"start_date": start_date,"end_date": end_date,"reason": reason,"status": status,"id": id})
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("update leaves set employee_id = %s, leave_type = %s, start_date = %s, end_date = %s, reason = %s, status = %s where id = %s",(employee_id,leave_type,start_date,end_date,reason,status,id))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Leave updated successfully.")
    return redirect(url_for("leaves.leaves_list"))

@leaves.route("/leaves/<int:id>/delete",methods=["POST"])
@login_required
def leaves_delete(id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("delete from leaves where id = %s",(id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Leave deleted successfully.")
    return redirect(url_for("leaves.leaves_list"))
