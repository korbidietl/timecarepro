from flask import Blueprint, render_template, request, redirect, url_for, flash
from db_query import (book_zeiteintrag, check_signatures, get_last_buchung,
                      get_zeiteintrag_for_client, get_first_te)
from datetime import datetime
from FMOF010_show_supervisionhours_client import extrahiere_jahr_und_monat

book_time_entry_blueprint = Blueprint('book_time_entry', __name__)


def get_next_month_to_book(last_buchung_date):

    if last_buchung_date:
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

    else:
        # 1 Monat für das Eintrag existiert wenn schon vergangen
        return


@book_time_entry_blueprint.route('/book_time_entries/<int:client_id>', methods=['POST'])
def book_client_time_entry(client_id):
    # Letzte Buchung abrufen
    last_month_booked = get_last_buchung(client_id)
    if last_month_booked is None:
        last_month_booked = get_first_te(client_id)
    next_month_to_book = get_next_month_to_book(last_month_booked)

    # überprüfe ob zeiteinträge für monat gefunden werden
    if not get_zeiteintrag_for_client(client_id, next_month_to_book):
        flash(f"Für den gebuchten Monat {next_month_to_book} existieren keine Zeiteinträge!")
        book_zeiteintrag(client_id)
        last_month_booked = get_last_buchung(client_id)
        flash(f"Stundennachweise für {last_month_booked} erfolgreich gebucht.")
        return render_template("FMOF010_show_supervisionhours_client.html")

    # überprüfen ob alle unterschriften vorhanden sind
    if not check_signatures(client_id, next_month_to_book):
        missing_signatures = check_signatures(client_id, next_month_to_book)
        flash(f"Unterschrift von Klient / Mitarbeiter < Klient / Mitarbeiter > in Eintrag {missing_signatures} fehlt."
              f"Buchung konnte nicht durchgeführt werden.")
        return render_template("FMOF010_show_supervisionhours_client.html")

    # Berechne Salden und führe Buchung durch
    if book_zeiteintrag(client_id):
        last_month_booked = get_last_buchung(client_id)
        flash(f"Stundennachweise für {last_month_booked} erfolgreich gebucht.")
        return render_template("FMOF010_show_supervisionhours_client.html")

    # Leite den Nutzer zurück zur Übersicht
    return redirect(url_for('FMOF010_show_supervisionhours_client', client_id=client_id))
