from flask import Blueprint, render_template, request, session
from db_query import get_client_ids, get_client_dashboard

show_clients_blueprint = Blueprint("show_clients", __name__, template_folder='templates')


@show_clients_blueprint.route('/show_clients', methods=['GET', 'POST'])
def show_clients():
    person = session['user_id']
    if request.method == 'POST':
        month = request.form['month']
        year = request.form['year']

        client_ids = get_client_ids(month, year, person)
        clients = []

        # Prüfen, ob Klienten-IDs vorhanden sind
        if not client_ids:
            return render_template('clients.html', person=person, clients=[],
                                   no_clients_message="Keine Klienten vorhanden.")

        for client_id in client_ids:
            client_info = get_client_dashboard(client_id, month, year)
            clients.append(client_info)

        return render_template('clients.html', person=person, clients=clients)
    else:
        return render_template('clients.html', person=person, clients=[])


