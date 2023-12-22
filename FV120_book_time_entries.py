from flask import Blueprint, render_template, request, redirect, url_for
from db_query import get_database_connection, book_zeiteintrag, check_signatures, check_month_booked
from FNAN010_login import logged_in_users
from datetime import datetime

book_time_entry_blueprint = Blueprint('book_time_entry', __name__)


@book_time_entry_blueprint.route('/book_time_entry', methods=['POST'])
def book_client_time_entry():

    client_id = request.form('client_id')
    # kombination jahr_monat --> hab noch nicht ganz verstanden wie das funktioniert
    datum = request.form('datum_jahr')

    if datum == time.strftime("%m.%Y")

    # Überprüfe, ob der Monat bereits gebucht wurde
    if check_month_booked(datum, client_id):
        # Schritt E1: Monat ist bereits gebucht
        return render_template('FMOF010_show_supervisionhours_client.html', error='Monat ist bereits gebucht.')


    # nächsten monat ermitteln
    next_month = last_booking['end_zeit'].month + 1
    year = last_booking['end_zeit'].year
    if next_month == 13:
        next_month = 1
        year += 1

    # Überprüfe Unterschriften
    if not check_signatures(client_id, next_month, year):
        # Schritt E3: Nicht alle Unterschriften vorhanden
        return render_template('FMOF010_show_supervisionhours_client.html',
                               error='Nicht alle Unterschriften vorhanden.')

    # Berechne Salden und führe Buchung durch
    booked = book_zeiteintrag(client_id)
    if not booked:
        # Schritt E2: Keine Zeiteinträge für den Monat gefunden
        return render_template('FMOF010_show_supervisionhours_client.html',
                               error='Keine Zeiteinträge für den Monat gefunden.')

    # Leite den Nutzer zurück zur Übersicht
    return redirect(url_for('FMOF010_show_supervisionhours_client', client_id=client_id))
