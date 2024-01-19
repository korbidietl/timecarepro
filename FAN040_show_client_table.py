from flask import Blueprint, request, session, jsonify
from db_query import get_client_table, get_client_table_sb, check_month_booked
from datetime import datetime

show_clients_blueprint = Blueprint("show_clients", __name__)


@show_clients_blueprint.route('/get_clients_data', methods=['GET'])
def get_clients_data():
    person = session.get('user_id')
    role = session.get('user_role')

    month = request.args.get('monat')
    year = request.args.get('jahr')

    month_int = int(month)
    year_int = int(year)

    datum = datetime(year_int, month_int, 1)

    if role == "Sachbearbeiter/Kostenträger":
        clients = get_client_table_sb(person, month, year)
        updated_clients = []
        for client in clients:
            client_list = list(client)  # Konvertiert das Tupel in eine Liste
            if not check_month_booked(datum, client_list[0]):
                message = (f"Noch kein Saldo vorhanden. Buchung zu Klient {client_list[1]}, {client_list[2]} "
                           f"muss erst vorgenommen werden.")
                client_list[5] = message
                client_list[6] = message
            updated_clients.append(client_list)
        return jsonify(updated_clients)
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


# test