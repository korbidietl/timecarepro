from flask import Blueprint, render_template, request, session
from db_query import get_client_table_client_sb, check_for_overlapping_zeiteintrag, check_booked

access_hours_km_clients_blueprint = Blueprint("access_hours_km_clients", __name__)


@access_hours_km_clients_blueprint.route('/access_hours_km_clients', methods=['GET', 'POST'])
def view_time_entries():
    client_id = 1
    person = 6
    messages = []
    zeiteintrag = []

    if request.method == 'POST':
        monat = 1 # request.form['month']
        jahr = 2024 # request.form['year']

        zeiteintrag_ids = get_client_table_client_sb(person, monat, jahr, client_id)

        for zeiteintrag in zeiteintrag_ids:
            zeiteintrag_id = zeiteintrag['id']  # Annahme: Jeder Zeiteintrag hat ein 'id'-Feld

            # Überprüfen auf Überschneidungen
            overlapping_ids = check_for_overlapping_zeiteintrag(zeiteintrag_id, client_id, zeiteintrag['start_time'],
                                                                zeiteintrag['end_time'])
            if overlapping_ids:
                messages.append(f"Überschneidung bei Zeiteintrag {zeiteintrag_id} mit {overlapping_ids}")

            # Überprüfen, ob gebucht
            if not check_booked(zeiteintrag_id):
                messages.append(f"Zeiteinträge für Monat {monat} wurden noch nicht gebucht")

            zeiteintrag.append(zeiteintrag)

    return render_template('FSK010_access_hours_km_clients.html',
                           person=person, zeiteintrag=zeiteintrag, messages=messages)
