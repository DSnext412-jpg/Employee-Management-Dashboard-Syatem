from flask import Blueprint,render_template,request,session,redirect,url_for
from config import get_db_connection,login_required
auth=Blueprint("auth",__name__)
@auth.route("/",methods=["GET"])
def index():
    return redirect(url_for("auth.login"))

@auth.route("/login",methods=["GET","POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))

    if request.method=="POST":
        username=request.form.get("username","").strip()
        password=request.form.get("password","").strip()

        if not username or not password:
            return render_template(
                "login.html",error="Username and password are required.",)

        conn=get_db_connection()
        cursor=conn.cursor()

        cursor.execute(
            "select id, username, email, password, role from users where username=%s or email=%s",(username,username),)
        user=cursor.fetchone()
        conn.close()

        if user and user["password"]==password:
            session["user_id"]=user["id"]
            session["username"]=user["username"]
            session["role"]=user["role"]
            return redirect(url_for("dashboard.dashboard"))
        else:
            return render_template(
                "login.html",error="Invalid username or password.",)

    return render_template("login.html")

@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
