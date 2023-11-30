from flask import Flask, render_template, request, redirect, url_for, session
from databaseConnection import get_database_connection, close_database_connection
from db_query import get_user_by_email #, get_password_for_user, get_role_for_user, get_locked_status
from einloggen import einloggen_blueprint
from password_reset import password_reset_blueprint

app = Flask(__name__)
app.secret_key = "yor_secret_key"

app.register_blueprint(einloggen_blueprint)
app.register_blueprint(password_reset_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
