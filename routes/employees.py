from flask import Blueprint,render_template,request,redirect,url_for,flash
from config import get_db_connection,login_required

employees=Blueprint("employees",__name__)

@employees.route("/employees")
@login_required
def employees_list():
    search_term=request.args.get("search","")
    conn=get_db_connection()
    cursor=conn.cursor()

    if search_term:
        like_term=f"%{search_term}%"
        cursor.execute("""
            select e.id, e.employee_id, e.first_name, e.last_name, e.email, e.phone,
                   e.position, d.name as department_name, e.status
            from employees e left join departments d on e.department_id = d.id
            where e.employee_id like %s or e.first_name like %s or e.last_name like %s
                  or e.email like %s or e.position like %s
            order by e.id desc
        """,(like_term,like_term,like_term,like_term,like_term))
    else:
        cursor.execute("""
            select e.id, e.employee_id, e.first_name, e.last_name, e.email, e.phone,
                   e.position, d.name as department_name, e.status
            from employees e left join departments d on e.department_id = d.id
            order by e.id desc
        """)

    emps=cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("employees.html",employees=emps,search_term=search_term)

@employees.route("/employees/add")
@login_required
def employees_add():
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("select id, name from departments order by name")
    departments=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("employee_form.html",employee_form_title="Add Employee",departments=departments)

@employees.route("/employees/add",methods=["POST"])
@login_required
def employees_add_post():
    employee_id=request.form.get("employee_id","").strip()
    first_name=request.form.get("first_name","").strip()
    last_name=request.form.get("last_name","").strip()
    email=request.form.get("email","").strip()
    phone=request.form.get("phone","").strip()
    gender=request.form.get("gender","").strip()
    date_of_birth=request.form.get("date_of_birth","").strip()
    address=request.form.get("address","").strip()
    position=request.form.get("position","").strip()
    salary=request.form.get("salary","").strip()
    hire_date=request.form.get("hire_date","").strip()
    department_id=request.form.get("department_id","").strip()
    status=request.form.get("status","").strip()

    validation_errors={}
    if not employee_id:
        validation_errors["employee_id"]="Employee ID is required."
    if not first_name:
        validation_errors["first_name"]="First Name is required."
    if not last_name:
        validation_errors["last_name"]="Last Name is required."
    if not email:
        validation_errors["email"]="Email is required."
    if not position:
        validation_errors["position"]="Position is required."
    if not hire_date:
        validation_errors["hire_date"]="Hire Date is required."
    if not department_id:
        validation_errors["department_id"]="Department is required."
    if employee_id:
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("select id from employees where employee_id = %s",(employee_id,))
        existing=cursor.fetchone()
        conn.close()
        if existing:
            validation_errors["employee_id"]="Employee ID already exists."

    if validation_errors:
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("select id, name from departments order by name")
        departments=cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("employee_form.html",employee_form_title="Add Employee",departments=departments,validation_errors=validation_errors,employee_employee_id=employee_id,employee_first_name=first_name,employee_last_name=last_name,employee_email=email,employee_phone=phone,employee_gender=gender,employee_dob=date_of_birth,employee_address=address,employee_position=position,employee_salary=salary,employee_hire_date=hire_date,employee_department_id=department_id,employee_status=status
        )

    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("""
        insert into employees (employee_id, first_name, last_name, email, phone, gender,
            date_of_birth, address, position, salary, hire_date, department_id, status)
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,(employee_id,first_name,last_name,email,phone,gender,date_of_birth,address,position,salary,hire_date,department_id,status))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Employee added successfully.")
    return redirect(url_for("employees.employees_list"))

@employees.route("/employees/<int:id>")
@login_required
def employee_details(id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("""
        select e.id, e.employee_id, e.first_name, e.last_name, e.email, e.phone,
               e.gender, e.date_of_birth, e.address, e.position, e.salary, e.hire_date,
               d.name as department_name, e.status
        from employees e left join departments d on e.department_id = d.id
        where e.id=%s
    """,(id,))
    employee=cursor.fetchone()
    cursor.close()
    conn.close()
    if not employee:
        flash("Employee not found.")
        return redirect(url_for("employees.employees_list"))

    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("""
        select e.id, e.employee_id, e.first_name, e.last_name, e.email, e.phone,
               e.position, d.name as department_name, e.status
        from employees e left join departments d on e.department_id = d.id
        order by e.id desc
    """)
    emps=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("employees.html",employees=emps,employee=employee,search_term="")

@employees.route("/employees/<int:id>/edit")
@login_required
def employee_edit(id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("""
        select e.id, e.employee_id, e.first_name, e.last_name, e.email, e.phone,
               e.gender, e.date_of_birth, e.address, e.position, e.salary, e.hire_date,
               e.department_id, e.status
        from employees e where e.id = %s
    """,(id,))
    employee=cursor.fetchone()
    if not employee:
        cursor.close()
        conn.close()
        flash("Employee not found.")
        return redirect(url_for("employees.employees_list"))
    cursor.execute("select id, name from departments order by name")
    departments=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("employee_form.html",employee_form_title="Edit Employee",employee=employee,departments=departments,employee_id=employee["id"],employee_employee_id=employee["employee_id"],employee_first_name=employee["first_name"],employee_last_name=employee["last_name"],employee_email=employee["email"],employee_phone=employee["phone"],employee_gender=employee["gender"],employee_dob=employee["date_of_birth"],employee_address=employee["address"],employee_position=employee["position"],employee_salary=employee["salary"],employee_hire_date=employee["hire_date"],employee_department_id=employee["department_id"],employee_status=employee["status"])

@employees.route("/employees/<int:id>/edit",methods=["POST"])
@login_required
def employee_edit_post(id):
    first_name=request.form.get("first_name","").strip()
    last_name=request.form.get("last_name","").strip()
    email=request.form.get("email","").strip()
    phone=request.form.get("phone","").strip()
    gender=request.form.get("gender","").strip()
    date_of_birth=request.form.get("date_of_birth","").strip()
    address=request.form.get("address","").strip()
    position=request.form.get("position","").strip()
    salary=request.form.get("salary","").strip()
    department_id=request.form.get("department_id","").strip()
    status=request.form.get("status","").strip()
    employee_id=request.form.get("employee_id","").strip()
    hire_date=request.form.get("hire_date","").strip()

    validation_errors={}
    if not employee_id:
        validation_errors["employee_id"]="Employee ID is required."
    if not first_name:
        validation_errors["first_name"]="First Name is required."
    if not last_name:
        validation_errors["last_name"]="Last Name is required."
    if not email:
        validation_errors["email"]="Email is required."
    if not position:
        validation_errors["position"]="Position is required."
    if not hire_date:
        validation_errors["hire_date"]="Hire Date is required."
    if not department_id:
        validation_errors["department_id"]="Department is required."
    if employee_id:
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("select id from employees where employee_id = %s and id != %s",(employee_id,id))
        existing=cursor.fetchone()
        conn.close()
        if existing:
            validation_errors["employee_id"]="Employee ID already exists."

    if validation_errors:
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("select id, name from departments order by name")
        departments=cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("employee_form.html",employee_form_title="Edit Employee",departments=departments,validation_errors=validation_errors,employee_id=id,employee_employee_id=employee_id,employee_first_name=first_name,employee_last_name=last_name,employee_email=email,employee_phone=phone,employee_gender=gender,employee_dob=date_of_birth,employee_address=address,employee_position=position,employee_salary=salary,employee_hire_date=hire_date,employee_department_id=department_id,employee_status=status
        )

    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("""
        update employees set employee_id=%s, first_name=%s, last_name=%s, email=%s,
            phone=%s, gender=%s, date_of_birth=%s, address=%s, position=%s,
            salary=%s, hire_date=%s, department_id=%s, status=%s
        where id=%s
    """,(employee_id,first_name,last_name,email,phone,gender,date_of_birth,address,position,salary,hire_date,department_id,status,id))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Employee updated successfully.")
    return redirect(url_for("employees.employee_details",id=id))

@employees.route("/employees/<int:id>/delete",methods=["POST"])
@login_required
def employee_delete(id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("delete from employees where id = %s",(id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Employee deleted successfully.")
    return redirect(url_for("employees.employees_list"))
