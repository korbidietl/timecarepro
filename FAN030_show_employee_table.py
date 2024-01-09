from flask import request, session, Blueprint, jsonify
from FAN040_show_client_table import generate_month_year_combinations
from db_query import account_table, account_table_mitarbeiter, get_unbooked_clients_for_month

show_employee_table_blueprint = Blueprint('show_employee_table', __name__)


@show_employee_table_blueprint.route('/get_employee_data', methods=['GET'])
def get_employee_data():
    person = session.get('user_id')
    role = session.get('user_role')

    month = request.args.get('monat')
    year = request.args.get('jahr')

    if role == "Mitarbeiter":
        mitarbeiter_liste = account_table_mitarbeiter(month, year, person)
        return jsonify(mitarbeiter_liste)
    elif role == "Steuerbüro":
        mitarbeiter_liste = account_table(month, year)
        if mitarbeiter_liste is None:
            missing_bookings = get_unbooked_clients_for_month(month, year)
            return jsonify(missing_bookings)
        else:
            return jsonify(mitarbeiter_liste)
    else:
        mitarbeiter_liste = account_table(month, year)
        return jsonify(mitarbeiter_liste)


@show_employee_table_blueprint.route('/get_employee_dropdown_data', methods=['GET'])
def get_dropdown_data():
    kombinationen = generate_month_year_combinations()

    return jsonify(kombinationen)


