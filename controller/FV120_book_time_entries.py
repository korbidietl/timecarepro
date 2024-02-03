from flask import Blueprint, render_template, redirect, url_for, flash, session
from model.buchung import get_last_buchung
from model.klient import get_klient_data
from model.person import get_person_data, get_steuerbuero_table, get_firstname_by_email, get_lastname_by_email
from model.zeiteintrag import get_zeiteintrag_for_client, check_and_return_signatures, get_first_te, book_zeiteintrag
from datetime import datetime
from model.mailserver_connection import send_email

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
    if 'user_id' in session:
        user_role = session['user_role']
        if user_role != 'Verwaltung' and user_role != 'Geschäftsführung':
            flash('Sie sind nicht berechtigt diese Seite aufzurufen.')
            return redirect(session['secure_url'])
        else:
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
            unvollstaendige_te = check_and_return_signatures(client_id, next_month, next_year)
            if unvollstaendige_te is True:
                # Überprüfen, ob Zeiteinträge für den nächsten Monat existieren
                if not get_zeiteintrag_for_client(client_id, next_month, next_year):
                    return render_template("FV120_book_time_entries.html", month_str=month_str,
                                           return_url=return_url, client_id=client_id)
                # Berechnen von Salden und Durchführen der Buchung
                if book_zeiteintrag(client_id):
                    create_and_send_email_list(client_id)
                    flash(f"Stundennachweise für {month_str} erfolgreich gebucht.")
                else:
                    flash("Fehler bei der Buchung.")
                return redirect(
                    url_for('client_hours_blueprint.client_supervision_hours', client_id=client_id))
            else:
                messages = []
                for entry in unvollstaendige_te:
                    entry_id = entry['id']
                    missing = ' und '.join(entry['missing'])  # Konvertiert die Liste in einen String
                    message = (
                        f"Unterschrift von {missing} in Eintrag {entry_id} fehlt. Buchung konnte nicht durchgeführt "
                        f"werden.")
                    messages.append(message)

                final_message = " ".join(messages)

                # Verwenden von flash, um die Nachricht anzuzeigen
                flash(final_message)
                return redirect(
                    url_for('client_hours_blueprint.client_supervision_hours', client_id=client_id))
    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))


@book_time_entry_blueprint.route('/confirm_booking/<int:client_id>', methods=['POST'])
def confirm_booking(client_id):
    if 'user_id' in session:
        user_role = session['user_role']
        if user_role != 'Verwaltung' and user_role != 'Geschäftsführung':
            flash('Sie sind nicht berechtigt diese Seite aufzurufen.')
            return redirect(session['secure_url'])
        else:
            if book_zeiteintrag(client_id):
                create_and_send_email_list(client_id)
                flash(f"Stundennachweise erfolgreich gebucht.")
            else:
                flash("Fehler bei der Buchung.")
            return redirect(
                url_for('client_hours_blueprint.client_supervision_hours', client_id=client_id))

    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))


def create_and_send_email_list(client_id):
    client_data = get_klient_data(client_id)
    client_first_name = client_data[0][1]
    client_last_name = client_data[0][2]
    booked_date = get_last_buchung(client_id)
    email_list = []
    date_str = booked_date[0]  # Angenommen, das Datum ist der erste Wert in der Rückgabe
    year, month = date_str.split('-')
    time_entries = get_zeiteintrag_for_client(client_id, month, year)
    # alle mitarbeiter emails der zeiteinträge hinzufügen
    for ze in time_entries:
        employee = ze[8]
        employee_data = list(get_person_data(employee))
        employee_email = employee_data[0][7]
        email_list.append(employee_email)
    # kostenträger mail hinzufügen
    kosten_id = client_data[0][5]
    if kosten_id:
        kosten_data = get_person_data(kosten_id)
        kosten_email = kosten_data[0][7]
        email_list.append(kosten_email)
    # steuerbüro mail hinzufügen
    steuer_liste = get_steuerbuero_table()
    for steuer in steuer_liste:
        steuer_id = steuer[0]
        steuer_data = get_person_data(steuer_id)
        steuer_email = steuer_data[0][7]
        email_list.append(steuer_email)
    subject = f"Zeiteintragbuchung {client_first_name} {client_last_name}, {month}/{year}"
    for email_adresse in email_list:
        firstname = get_firstname_by_email(email_adresse)
        lastname = get_lastname_by_email(email_adresse)
        body = (f"Sehr geehrte/r {firstname} {lastname}, \n\n"
                f"Die Zeiteinträge des Klienten {client_last_name}, {client_first_name} wurden für den Monat "
                f"{month}/{year} gebucht. \n\n"
                f"Freundliche Grüße\n"
                f"Ihr TimeCare Pro-Team")
        send_email(email_adresse, subject, body)