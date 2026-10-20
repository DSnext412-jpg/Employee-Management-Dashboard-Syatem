from flask import Blueprint,render_template,request,redirect,url_for,flash
from config import get_db_connection,login_required

departments=Blueprint("departments",__name__)

@departments.route("/departments")
@login_required
def departments_list():
    search_term=request.args.get("search","")
    conn=get_db_connection()
    cursor=conn.cursor()
    if search_term:
        like_term=f"%{search_term}%"
        cursor.execute("""
            select d.id, d.name, d.description, count(e.id) as employee_count
            from departments d left join employees e on d.id = e.department_id
            where lower(d.name) like lower(%s) or lower(d.description) like lower(%s)
            group by d.id, d.name, d.description order by d.name
        """,(like_term,like_term))
    else:
        cursor.execute("""
            select d.id, d.name, d.description, count(e.id) as employee_count
            from departments d left join employees e on d.id = e.department_id
            group by d.id, d.name, d.description order by d.name
        """)
    depts=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("departments.html",departments=depts,search_term=search_term)

@departments.route("/departments/add")
@login_required
def departments_add():
    return render_template("department_form.html",department_form_title="Add Department")

@departments.route("/departments/add",methods=["POST"])
@login_required
def departments_add_post():
    department_name=request.form.get("department_name","").strip()
    department_description=request.form.get("department_description","").strip()
    validation_errors={}
    if not department_name:
        validation_errors["name"]="Department name is required."
    if validation_errors:
        return render_template("department_form.html",department_form_title="Add Department",validation_errors=validation_errors,department_name=department_name,department_description=department_description
        )
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("insert into departments (name, description) values (%s, %s)",(department_name,department_description))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Department added successfully.")
    return redirect(url_for("departments.departments_list"))

@departments.route("/departments/<int:id>")
@login_required
def department_details(id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("""
        select d.id, d.name, d.description, d.created_at, count(e.id) as employee_count
        from departments d left join employees e on d.id = e.department_id
        where d.id=%s group by d.id, d.name, d.description, d.created_at
    """,(id,))
    department=cursor.fetchone()
    if not department:
        cursor.close()
        conn.close()
        flash("Department not found.")
        return redirect(url_for("departments.departments_list"))
    cursor.execute("""
        select e.employee_id, e.first_name, e.last_name, e.position, e.status
        from employees e where e.department_id = %s order by e.first_name, e.last_name
    """,(id,))
    dept_employees=cursor.fetchall()
    cursor.execute("""
        select d.id, d.name, d.description, count(e.id) as employee_count
        from departments d left join employees e on d.id = e.department_id
        group by d.id, d.name, d.description order by d.name
    """)
    depts=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("departments.html",departments=depts,department=department,department_employees=dept_employees,search_term="")

@departments.route("/departments/<int:id>/edit")
@login_required
def departments_edit(id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("select * from departments where id = %s",(id,))
    department=cursor.fetchone()
    if not department:
        cursor.close()
        conn.close()
        flash("Department not found.")
        return redirect(url_for("departments.departments_list"))
    cursor.close()
    conn.close()
    return render_template("department_form.html",department_form_title="Edit Department",department=department,department_id=department["id"],department_name=department["name"],department_description=department["description"])

@departments.route("/departments/<int:id>/edit",methods=["POST"])
@login_required
def departments_edit_post(id):
    department_name=request.form.get("department_name","").strip()
    department_description=request.form.get("department_description","").strip()
    validation_errors={}
    if not department_name:
        validation_errors["name"]="Department name is required."
    if validation_errors:
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("select * from departments where id = %s",(id,))
        department=cursor.fetchone()
        cursor.close()
        conn.close()
        if not department:
            flash("Department not found.")
            return redirect(url_for("departments.departments_list"))
        return render_template("department_form.html",department_form_title="Edit Department",department=department,department_id=id,validation_errors=validation_errors,department_name=department_name,department_description=department_description
        )
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("update departments set name = %s, description = %s where id = %s",(department_name,department_description,id))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Department updated successfully.")
    return redirect(url_for("departments.departments_list"))

@departments.route("/departments/<int:id>/delete",methods=["POST"])
@login_required
def departments_delete(id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("delete from departments where id = %s",(id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Department deleted successfully.")
    return redirect(url_for("departments.departments_list"))
