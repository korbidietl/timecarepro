from flask import Flask
from datetime import timedelta
from session_check import check_session_timeout


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = "secretKey"

    # für die Inaktivitätsbedingung
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.before_request(check_session_timeout)

    # Systemweite Anforderungen
    from FS020_sign_capture import signature_blueprint
    app.register_blueprint(signature_blueprint)

    # Nicht-angemeldete Nutzer
    from FNAN010_login import login_blueprint
    app.register_blueprint(login_blueprint)

    from FNAN020_password_reset import password_reset_blueprint
    app.register_blueprint(password_reset_blueprint)

    # Angemeldete Nutzer
    from FAN010_home import home_blueprint
    app.register_blueprint(home_blueprint)

    from FAN030_show_employee_table import show_employee_table_blueprint
    app.register_blueprint(show_employee_table_blueprint)

    from FAN040_show_client_table import show_clients_blueprint
    app.register_blueprint(show_clients_blueprint)

    from FAN050_logout import logout_blueprint
    app.register_blueprint(logout_blueprint)

    from FAN060_password_change import password_change_blueprint
    app.register_blueprint(password_change_blueprint)

    # Mitarbeiter ohne Fallverantwortung
    from FMOF010_show_supervisionhours_client import client_hours_blueprint
    app.register_blueprint(client_hours_blueprint)

    from FMOF020_view_time_entries import view_time_entries_blueprint
    app.register_blueprint(view_time_entries_blueprint)

    from FMOF030_create_time_entry import create_time_entry_blueprint
    app.register_blueprint(create_time_entry_blueprint)

    from FMOF040_work_hours_details import work_hours_details_blueprint
    app.register_blueprint(work_hours_details_blueprint)

    from FMOF050_edit_time_entry import edit_time_entry_blueprint
    app.register_blueprint(edit_time_entry_blueprint)

    from FMOF060_delete_time_entry import delete_time_entry_blueprint
    app.register_blueprint(delete_time_entry_blueprint)

    # Verwaltung
    from FV010_account_management import account_management_blueprint
    app.register_blueprint(account_management_blueprint)

    from FV020_create_account import create_account_blueprint
    app.register_blueprint(create_account_blueprint)

    from FV030_account_details import account_details_blueprint
    app.register_blueprint(account_details_blueprint)

    from FV040_edit_account import edit_account_blueprint
    app.register_blueprint(edit_account_blueprint)

    from FV050_account_lock import account_lock_blueprint
    app.register_blueprint(account_lock_blueprint)

    from FV060_account_unlock import account_unlock_blueprint
    app.register_blueprint(account_unlock_blueprint)

    from FV070_create_client import create_client_blueprint
    app.register_blueprint(create_client_blueprint)

    from FV080_client_details import client_details_blueprint
    app.register_blueprint(client_details_blueprint)

    from FV090_edit_client import edit_client_blueprint
    app.register_blueprint(edit_client_blueprint)

    from FV100_edit_time_entry_fv import edit_time_entry_fv_blueprint
    app.register_blueprint(edit_time_entry_fv_blueprint)

    # Geschäftsführung
    from FGF010_view_reporting_dashboard import reporting_dachboard_blueprint
    app.register_blueprint(reporting_dachboard_blueprint)

    from FGF020_show_protocol import show_protocol_blueprint
    app.register_blueprint(show_protocol_blueprint)

    # Kostenträger/Sachbearbeiter
    from FSK010_access_hours_km_clients import access_hours_km_clients_blueprint
    app.register_blueprint(access_hours_km_clients_blueprint)

    return app


app = create_app()

for rule in app.url_map.iter_rules():
    print(rule)

if __name__ == '__main__':
    app.run(debug=True)