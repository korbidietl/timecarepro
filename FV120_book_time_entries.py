from flask import Blueprint, render_template, request, redirect, url_for, flash
from db_query import (book_zeiteintrag, check_signatures, get_last_buchung,
                      get_zeiteintrag_for_client, get_first_te)
from datetime import datetime

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

    # Aufteilen von next_month_to_book in Jahr und Monat
    next_year, next_month = next_month_to_book.split('-')
    next_month = int(next_month)
    next_year = int(next_year)

    # Überprüfen, ob Zeiteinträge für den nächsten Monat existieren
    if not get_zeiteintrag_for_client(client_id, next_month, next_year):
        flash(f"Für den Monat {next_month_to_book} existieren keine Zeiteinträge!")

    # Überprüfen, ob alle Unterschriften vorhanden sind
    unvollständige_te = check_and_return_signatures(client_id, next_month, next_year)
    if not unvollständige_te is None:
        for entries in unvollständige_te:
            zeiteintrag = get_zeiteintrag_by_id(entries)
            if zeiteintrag[1] is None:
                flash(f"Unterschrift von Mitarbeiter Nr. {zeiteintrag[5]} in Eintrag {zeiteintrag} fehlt.")
            elif zeiteintrag[2] is None:
                flash(f"Unterschrift von Klient Nr. {zeiteintrag[6]} in Eintrag {zeiteintrag} fehlt.")
        return render_template("FMOF010_show_supervisionhours_client.html", client_id=client_id)


    # Berechnen von Salden und Durchführen der Buchung
    if book_zeiteintrag(client_id):
        flash(f"Stundennachweise für {next_month_to_book} erfolgreich gebucht.")
    else:
        flash("Fehler bei der Buchung.")

    return redirect(url_for('FMOF010_show_supervisionhours_client.show_supervisionhours_client', client_id=client_id))

