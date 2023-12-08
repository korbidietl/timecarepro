from flask import Flask, render_template
from datetime import timedelta
# from middleware import before_request


# alle Blueprints
def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.secret_key = "your_secret_key"

    # für die Inaktivitätsbedingung
    # app.config['SESSION_TYPE'] = 'filesystem'  # Du kannst 'filesystem' durch andere Optionen ersetzen
    # app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Setze die Inaktivitätszeit auf 30 Minuten

    from login import login_blueprint
    app.register_blueprint(login_blueprint, url_prefix='/login')

    from password_reset import password_reset_blueprint
    app.register_blueprint(password_reset_blueprint, url_prefix='/password_reset')

    return app


app = create_app()


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


@app.route("/create_client")
def create_client():
    return render_template("create_client.html")


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
