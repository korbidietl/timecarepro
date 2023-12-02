from flask import Flask, session, render_template
from login import einloggen_blueprint
from password_reset import password_reset_blueprint
from logout import logout_blueprint
# from flask_session import Session
from datetime import timedelta
from middleware import before_request
from db_query import sachbearbeiter_dropdown

app = Flask(__name__)
app.secret_key = "your_secret_key"

# für die Inaktivitätsbedingung
app.config['SESSION_TYPE'] = 'filesystem'  # Du kannst 'filesystem' durch andere Optionen ersetzen
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Setze die Inaktivitätszeit auf 30 Minuten


# alle Blueprints
app.register_blueprint(einloggen_blueprint)
app.register_blueprint(password_reset_blueprint)
app.register_blueprint(logout_blueprint)


session(app)

# Middleware registrieren
app.before_request(before_request)

if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True)
