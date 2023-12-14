from flask import Blueprint, render_template, request, session
from db_query import get_client_table, get_client_table_sb

show_clients_blueprint = Blueprint("show_clients", __name__, template_folder='templates')


@show_clients_blueprint.route('/show_clients', methods=['GET', 'POST'])
def show_clients():
    person = session['user_id']
    role = session['user_role']

    if request.method == 'POST':
        month = request.form['month']
        year = request.form['year']

        if role == "Sachbearbeiter/Kostenträger":
            clients = get_client_table_sb(person, month, year)
        else:
            clients = get_client_table(month, year)

        if not clients:
            return render_template('FAN040_show_client_table.html', person=person, clients=[], no_clients_message="Keine Klienten vorhanden.")

        return render_template('FAN040_show_client_table.html', person=person, clients=clients)

    else:
        return render_template('FAN040_show_client_table.html', person=person, clients=[])


