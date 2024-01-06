from flask import Blueprint, request, session, jsonify
from db_query import get_client_table, get_client_table_sb
from datetime import datetime

show_clients_blueprint = Blueprint("show_clients", __name__)


@show_clients_blueprint.route('/get_clients_data', methods=['GET'])
def get_clients_data():
    person = session.get('user_id')
    role = session.get('user_role')

    month = request.args.get('monat')
    year = request.args.get('jahr')

    if role == "Sachbearbeiter/Kostenträger":
        clients = get_client_table_sb(person, month, year)
        print(clients)
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
