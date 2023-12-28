from flask import Blueprint, render_template, request, redirect, url_for, flash
from db_query import (book_zeiteintrag, check_signatures, check_month_booked, get_last_buchung,
                      is_booked_client,  get_zeiteintrag_for_client) # get_first_time_entry,
from FNAN010_login import logged_in_users
from datetime import datetime

book_time_entry_blueprint = Blueprint('book_time_entry', __name__)


def get_next_month_to_book(last_buchung_date):
    # Konvertieren des Datumsstrings in ein datetime-Objekt
    last_date_obj = datetime.strptime(last_buchung_date, '%Y-%m')

    # Berechnung des nächsten Monats
    year, month = last_date_obj.year, last_date_obj.month
    if month == 12:
        next_month_date_obj = datetime(year + 1, 1, 1)
    else:
        next_month_date_obj = datetime(year, month + 1, 1)

    # Rückumwandlung in einen String
    next_month_str = next_month_date_obj.strftime('%Y-%m')
    return next_month_str



@book_time_entry_blueprint.route('/book_time_entries/<int:client_id>', methods=['POST'])
def book_client_time_entry(client_id):

    # kombination jahr_monat --> hab noch nicht ganz verstanden wie das funktioniert
    datum = request.form('datum_jahr')

    last_month_booked = get_last_buchung(client_id)
    next_month_to_book = get_next_month_to_book(last_month_booked)
    # es wurde noch kein monat gebucht
    if not is_booked_client(client_id, datum):
        print("Hallo")
        # next_month_to_book = get_first_time_entry(client_id)

    # ausgewählter monat ist nicht last_month_booked + 1 / es wurde noch kein monat gebucht
    if datum != next_month_to_book:
        flash(f"Bitte buchen sie erst alle Monate seit {next_month_to_book} bevor sie {datum} buchen!")
        return render_template("FMOF010_show_supervisionhours_client.html")

    # ausgewählter monat wurde bereits gebucht
    if datum == last_month_booked:
        flash(f"Der Monat {datum} wurde bereits gebucht!")
        return render_template("FMOF010_show_supervisionhours_client.html")

    # überprüfe ob zeiteinträge für monat gefunden werden
    if not get_zeiteintrag_for_client(client_id, datum):
        flash(f"Für den ausgewählten Monat {datum} existieren keine Zeiteinträge!")
        return render_template("FMOF010_show_supervisionhours_client.html")

    # überprüfen ob alle unterschriften vorhanden sind
    if not check_signatures(client_id, datum):
        missing_signatures = check_signatures(client_id, datum)
        flash(f"Unterschrift von Klient / Mitarbeiter < Klient / Mitarbeiter > in Eintrag {missing_signatures} fehlt."
              f"Buchung konnte nicht durchgeführt werden.")
        return render_template("FMOF010_show_supervisionhours_client.html")

    # Berechne Salden und führe Buchung durch
    if book_zeiteintrag(client_id):
        flash(f"Stundennachweise für {datum} erfolgreich gebucht.")
        return render_template("FMOF010_show_supervisionhours_client.html")

    # Leite den Nutzer zurück zur Übersicht
    return redirect(url_for('FMOF010_show_supervisionhours_client', client_id=client_id))
