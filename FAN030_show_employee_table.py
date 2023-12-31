from datetime import datetime

from flask import render_template, request, session, Blueprint, flash
from db_query import account_table, account_table_mitarbeiter, get_role_by_id
from FMOF010_show_supervisionhours_client import generate_month_year_combinations, extrahiere_jahr_und_monat

show_employee_table_blueprint = Blueprint('show_employee_table', __name__)


@show_employee_table_blueprint.route('/show_employee_table/<int:person_id>', methods=['GET', 'POST'])
def mitarbeiter(person_id):
    user_role = get_role_by_id(person_id)
    # user_role = get_role_by_id(session.get('user_id'))
    mitarbeiterliste = []

    kombinationen = generate_month_year_combinations()
    aktuelles_jahr = datetime.now().year
    aktueller_monat = datetime.now().month

    # auswahl des angezeigten Zeitraums
    if request.method == 'POST':
        gewaehlte_kombination = request.form.get('monat_jahr')
    else:
        # Standardmäßig aktuelles Monat und Jahr
        monate = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                  'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']

        gewaehlte_kombination = f"{monate[aktueller_monat - 1]} {aktuelles_jahr}"

    month, year = extrahiere_jahr_und_monat(gewaehlte_kombination)

    if user_role in ["Steuerbüro", "Geschäftsführung"]:
        mitarbeiterliste = account_table(month, year)
    elif user_role == "Mitarbeiter":
        mitarbeiterliste = account_table_mitarbeiter(month, year, session['user_id'])
    else:
        # Optionale Handhabung für andere Rollen oder Fehlermeldung
        pass

    # Fehlerbehandlung, wenn keine Mitarbeiter gefunden werden
    if not mitarbeiterliste:
        flash("Keine Mitarbeiter gefunden.")
        return render_template('FAN030_show_employee_table.html',
                               kombinationen=kombinationen, gewaehlte_kombination=gewaehlte_kombination)

    return render_template('FAN030_show_employee_table.html',
                           mitarbeiterliste=mitarbeiterliste, kombinationen=kombinationen,
                           gewaehlte_kombination=gewaehlte_kombination)



