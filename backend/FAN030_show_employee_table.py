from flask import render_template, request, session, Blueprint
from db_query import account_table, account_table_mitarbeiter, get_role_by_id

show_employee_table_blueprint = Blueprint('show_employee_table', __name__)


@show_employee_table_blueprint.route('/show_employee_table', methods=['GET', 'POST'])
def mitarbeiter():
    user_role = get_role_by_id(session['user_id'])
    mitarbeiterliste = []

    if request.method == 'POST':

        monat = request.form['zeitraum']

        if user_role in ["Steuerbüro", "Geschäftsführung"]:
            mitarbeiterliste = account_table(monat)
        elif user_role == "Mitarbeiter":
            mitarbeiterliste = account_table_mitarbeiter(monat, session['user_id'])
        else:
            # Optionale Handhabung für andere Rollen oder Fehlermeldung
            pass

    # Fehlerbehandlung, wenn keine Mitarbeiter gefunden werden
    if not mitarbeiterliste:
        return render_template('FAN030_show_employee_table.html', error_message="Keine Mitarbeiter gefunden.")

    return render_template('FAN030_show_employee_table.html', mitarbeiterliste=mitarbeiterliste)



