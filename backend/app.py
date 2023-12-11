from flask import Flask
from datetime import timedelta


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = "secretKey"

    # für die Inaktivitätsbedingung
    # app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    # app.before_request(check_session_timeout)

    # Systemweite Anforderungen
    from sign_capture import signature_blueprint
    app.register_blueprint(signature_blueprint)

    # Nicht-angemeldete Nutzer
    from login import login_blueprint
    app.register_blueprint(login_blueprint)

    from password_reset import password_reset_blueprint
    app.register_blueprint(password_reset_blueprint)

    # Angemeldete Nutzer
    from home import home_blueprint
    app.register_blueprint(home_blueprint)

    from logout import logout_blueprint
    app.register_blueprint(logout_blueprint)

    from password_change import password_change_blueprint
    app.register_blueprint(password_change_blueprint)

    # Sachbearbeiter/Kostenträger

    # Mitarbeiter ohne Fallverantwortung
    from show_supervisionhours_client import client_hours_blueprint
    app.register_blueprint(client_hours_blueprint)

    from create_time_entry import create_time_entry_blueprint
    app.register_blueprint(create_time_entry_blueprint)

    from edit_time_entry import edit_time_entry_blueprint
    app.register_blueprint(edit_time_entry_blueprint)

    from delete_time_entry import delete_time_entry_blueprint
    app.register_blueprint(delete_time_entry_blueprint)

    # Verwaltung
    from create_account import create_account_blueprint
    app.register_blueprint(create_account_blueprint)

    from edit_account import edit_account_blueprint
    app.register_blueprint(edit_account_blueprint)

    from create_client import create_client_blueprint
    app.register_blueprint(create_client_blueprint)

    from edit_client import edit_client_blueprint
    app.register_blueprint(edit_client_blueprint)

    # Geschäftsführung

    return app


app = create_app()

for rule in app.url_map.iter_rules():
    print(rule)

if __name__ == '__main__':
    app.run(debug=True)
