from datetime import datetime

from flask import render_template, request, session, Blueprint, flash, jsonify

from FAN040_show_client_table import generate_month_year_combinations
from db_query import account_table, account_table_mitarbeiter, get_role_by_id
from FMOF010_show_supervisionhours_client import extrahiere_jahr_und_monat

show_employee_table_blueprint = Blueprint('show_employee_table', __name__)


@show_employee_table_blueprint.route('/get_employee_data', methods=['GET'])
def get_employee_data():
    person = session.get('user_id')
    role = session.get('user_role')

    month = request.args.get('monat')
    year = request.args.get('jahr')
    print('Hallo')
    print(role)


    if role in ["Steuerbüro", "Verwaltung", "Geschäftsführung"]:
        mitarbeiter = account_table(month, year)
        print('after:' )
        print(mitarbeiter)
    elif role == "Mitarbeiter":
        mitarbeiter = account_table_mitarbeiter(month, year, person)
        print(mitarbeiter)
    else:
        flash("Sie sind nicht erlaubt diese Tabelle zu sehen")
        return render_template('FAN010_home.html')

    return jsonify(mitarbeiter)


@show_employee_table_blueprint.route('/get_employee_dropdown_data', methods=['GET'])
def get_dropdown_data():
    kombinationen = generate_month_year_combinations()

    return jsonify(kombinationen)


@show_employee_table_blueprint.route('/show_employee_table', methods=['GET', 'POST'])
def mitarbeiter():
    person_id = session.get('user_id')
    user_role = get_role_by_id(person_id)
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

    # Füllen der Mitarbeiterliste
    if user_role in ["Steuerbüro", "Verwaltung", "Geschäftsführung"]:
        mitarbeiterliste = account_table(month, year)
        print(mitarbeiterliste)
    elif user_role == "Mitarbeiter":
        mitarbeiterliste = account_table_mitarbeiter(month, year, person_id)
        print(mitarbeiterliste)
    else:
        # Optionale Handhabung für andere Rollen oder Fehlermeldung
        pass

    return render_template('FAN030_show_employee_table.html',
                           mitarbeiterliste=mitarbeiterliste, kombinationen=kombinationen,
                           gewaehlte_kombination=gewaehlte_kombination, user_role=user_role, person_id=person_id)
