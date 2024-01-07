from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db_query import (book_zeiteintrag, get_last_buchung, get_zeiteintrag_by_id, get_name_by_id,
                      get_zeiteintrag_for_client, get_first_te, check_and_return_signatures)
from datetime import datetime

book_time_entry_blueprint = Blueprint('book_time_entry', __name__)


def get_next_month_to_book(last_buchung_date):

    if last_buchung_date:
        # Konvertieren des Datumsstrings in ein datetime-Objekt
        last_date_obj = datetime.strptime(last_buchung_date[0], '%Y-%m')

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


def month_number_to_name(month_number):
    # Eine Liste der Monatsnamen, wobei der Index 0 leer ist, da Monate von 1 bis 12 nummeriert sind
    month_names = ["", "Januar", "Februar", "März", "April", "Mai", "Juni",
                   "Juli", "August", "September", "Oktober", "November", "Dezember"]

    # Stellen Sie sicher, dass der Monat innerhalb des gültigen Bereichs liegt
    if 1 <= month_number <= 12:
        return month_names[month_number]
    else:
        return None  # oder eine geeignete Fehlermeldung oder -behandlung


@book_time_entry_blueprint.route('/book_time_entries/<int:client_id>', methods=['POST'])
def book_client_time_entry(client_id):
    return_url = session.get('url')
    # Letzte Buchung abrufen
    last_month_booked = get_last_buchung(client_id)
    if last_month_booked is None:
        next_month_to_book = get_first_te(client_id)
    else:
        next_month_to_book = get_next_month_to_book(last_month_booked)

    # Aufteilen von next_month_to_book in Jahr und Monat
    next_year, next_month = next_month_to_book.split('-')
    next_month = int(next_month)
    next_year = int(next_year)

    month_str = month_number_to_name(next_month)

    # Überprüfen, ob alle Unterschriften vorhanden sind
    unvollständige_te = check_and_return_signatures(client_id, next_month, next_year)
    if unvollständige_te is True:
        # Überprüfen, ob Zeiteinträge für den nächsten Monat existieren
        if not get_zeiteintrag_for_client(client_id, next_month, next_year):
            return render_template("FV120_book_time_entries.html", month_str=month_str, return_url=return_url)
        # Berechnen von Salden und Durchführen der Buchung
        if book_zeiteintrag(client_id):
            print("gebucht")
            flash(f"Stundennachweise für {month_str} erfolgreich gebucht.")
        else:
            flash("Fehler bei der Buchung.")
        return redirect(
            url_for('client_hours_blueprint.client_supervision_hours', client_id=client_id))
    else:
        messages = []
        for entry in unvollständige_te:
            entry_id = entry['id']
            missing = ' und '.join(entry['missing'])  # Konvertiert die Liste in einen String
            message = f"Unterschrift von {missing} in Eintrag {entry_id} fehlt. Buchung konnte nicht durchgeführt werden."
            messages.append(message)

        final_message = " ".join(messages)

        # Verwenden von flash, um die Nachricht anzuzeigen
        flash(final_message)
        return redirect(
            url_for('client_hours_blueprint.client_supervision_hours', client_id=client_id))


@book_time_entry_blueprint.route('/confirm_booking/<int:client_id>', methods=['POST'])
def confirm_booking(client_id):
    if book_zeiteintrag(client_id):
        flash(f"Stundennachweise erfolgreich gebucht.")
    else:
        flash("Fehler bei der Buchung.")
    return redirect(
        url_for('client_hours_blueprint.client_supervision_hours', client_id=client_id))



