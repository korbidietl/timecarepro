from flask import Blueprint, render_template, request, session, jsonify
from db_query import get_client_table, get_client_table_sb
from FMOF010_show_supervisionhours_client import extrahiere_jahr_und_monat
from datetime import datetime

show_clients_blueprint = Blueprint("show_clients", __name__)


@show_clients_blueprint.route('/show_clients', methods=['GET', 'POST'])
def show_clients():
    person = session.get('user_id')
    role = session.get('user_role')

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

    if role == "Sachbearbeiter/Kostenträger":
        clients = get_client_table_sb(person, month, year)
    else:
        clients = get_client_table(month, year)
    if not clients:
        return render_template('FAN040_show_client_table.html', person=person, clients=[],
                               gewaehlte_kombination=gewaehlte_kombination, kombinationen=kombinationen, role=role,
                               no_clients_message="Keine Klienten vorhanden.")

    print(clients)

    return render_template('FAN040_show_client_table.html', person=person, clients=clients,
                           gewaehlte_kombination=gewaehlte_kombination, kombinationen=kombinationen, role=role)


@show_clients_blueprint.route('/get_clients_data', methods=['GET'])
def get_clients_data():
    person = session.get('user_id')
    role = session.get('user_role')

    month = request.args.get('monat')
    year = request.args.get('jahr')
    print(month)
    print(year)

    if role == "Sachbearbeiter/Kostenträger":
        clients = get_client_table_sb(person, month, year)
    else:
        clients = get_client_table(month, year)

    return jsonify(clients)


@show_clients_blueprint.route('/get_client_dropdown_data', methods=['GET'])
def get_dropdown_data():
    kombinationen = generate_month_year_combinations()

    return jsonify(kombinationen)


def generate_month_year_combinations():
    aktuelles_jahr = datetime.now().year
    aktueller_monat = datetime.now().month
    monate = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
              'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']

    # Generiere Kombinationen
    kombinationen = [f"{monat} {jahr}" for jahr in range(2020, aktuelles_jahr + 1) for monat in monate]

    # Stelle sicher, dass die Kombinationen für das aktuelle Jahr nur bis zum aktuellen Monat gehen
    if aktuelles_jahr == datetime.now().year:
        kombinationen = [k for k in kombinationen if
                         not (k.endswith(str(aktuelles_jahr)) and monate.index(k.split(" ")[0]) >= aktueller_monat)]

    return kombinationen
