from flask import Flask, render_template, request
from datetime import timedelta
from session_check import check_session_timeout


# alle Blueprints
def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = "secretKey"

    # für die Inaktivitätsbedingung
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    # app.before_request(check_session_timeout)

    from login import login_blueprint
    app.register_blueprint(login_blueprint)

    from password_reset import password_reset_blueprint
    app.register_blueprint(password_reset_blueprint)

    from show_supervisionhours_client import client_hours_blueprint
    app.register_blueprint(client_hours_blueprint)
    return app


app = create_app()

for rule in app.url_map.iter_rules():
    print(rule)

# app.register_blueprint(password_reset_blueprint)
# app.register_blueprint(logout_blueprint)


#@app.route("/login")
#def log():
#    return render_template('login.html')


# @app.route("/password_reset")
# def password_reset():
#   return render_template("password_reset.html")


# @app.route("/create_account")
# def create_account():
#   return render_template("create_account.html")


#@app.route("/create_client")
#def create_client():
#   return render_template("create_client.html")


#
#
# @app.route("/create_time_entry")
# def create_time_entry():
#     return render_template("create_time_entry.html")
#
#
# @app.route("/edit_client")
# def edit_client():
#     return render_template("edit_client.html")
#
#
# @app.route("/password_change")
# def password_change():
#     return render_template("password_change.html")
#
#
# @app.route("/password_reset")
# def password_reset():
#     return render_template("password_reset.html")


# @app.route("/login", methods=["POST"])
# def after_login():
#     form_dict = request.form.to_dict()
#     password = form_dict.get("password")
#     email = form_dict.get("email")
#
#
#
#     return render_template("login.html")


# session(app)

# Middleware registrieren
# app.before_request(before_request)

if __name__ == '__main__':
    app.run(debug=True)
