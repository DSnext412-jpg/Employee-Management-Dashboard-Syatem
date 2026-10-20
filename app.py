from flask import Flask
from config import Config

app=Flask(__name__)
app.config.from_object(Config)

from routes.auth import auth
from routes.dashboard import dashboard_bp as dashboard
from routes.employees import employees
from routes.departments import departments
from routes.attendance import attendance
from routes.leaves import leaves

app.register_blueprint(auth)
app.register_blueprint(dashboard)
app.register_blueprint(employees)
app.register_blueprint(departments)
app.register_blueprint(attendance)
app.register_blueprint(leaves)

if __name__== "__main__":
    app.run(debug=Config.DEBUG)
