import os
from dotenv import load_dotenv
import MySQLdb
from MySQLdb.cursors import DictCursor
from functools import wraps
from flask import session,redirect,url_for,request,make_response

load_dotenv()

MYSQL_HOST=os.getenv("MYSQL_HOST","localhost")
MYSQL_USER=os.getenv("MYSQL_USER","root")
MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD","")
MYSQL_DB=os.getenv("MYSQL_DB","employee360")
MYSQL_PORT=int(os.getenv("MYSQL_PORT",3306))

SECRET_KEY=os.getenv("SECRET_KEY","a-dev-secret-key-change-in-production")
DEBUG=os.getenv("DEBUG","True").lower()=="true"

class Config:
    SECRET_KEY=SECRET_KEY
    DEBUG=DEBUG
    MYSQL_HOST=MYSQL_HOST
    MYSQL_USER=MYSQL_USER
    MYSQL_PASSWORD=MYSQL_PASSWORD
    MYSQL_DB=MYSQL_DB
    MYSQL_PORT=MYSQL_PORT

def get_db_connection():
    return MySQLdb.connect(
        host=MYSQL_HOST,user=MYSQL_USER,passwd=MYSQL_PASSWORD,db=MYSQL_DB,port=MYSQL_PORT,cursorclass=DictCursor,)

def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login",next=request.url))
        response=make_response(f(*args,**kwargs))
        response.headers["Cache-Control"]="no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"]="no-cache"
        response.headers["Expires"]="0"
        return response
    return decorated_function