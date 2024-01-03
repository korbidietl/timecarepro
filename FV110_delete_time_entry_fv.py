import smtplib
from email.mime.text import MIMEText

from flask import Blueprint, request, flash, redirect, url_for, render_template, session
from db_query import check_booked, delete_zeiteintrag, get_email_by_zeiteintrag, get_lastname_by_email

delete_time_entry_fv_blueprint = Blueprint("delete", __name__)


def send_email(email, subject, body):
    msg = MIMEText(body)

    msg['Subject'] = subject
    msg['From'] = 'deletetimeentry@timecarepro.de'
    msg['To'] = email

    with smtplib.SMTP('132.231.36.210', 1103) as smtp:
        smtp.login('mailhog_grup3', 'Uni75Winfo17Master')
        smtp.sendmail('deletetimeentry@timecarepro.de', [email], msg.as_string())


def send_email_delete_time_entry(email, lastname, id):
    subject = "Gelöschter Zeiteintrag"
    body = (f"Sehr geehrte/r Frau/Mann {lastname}, \n\n"
            f"Ihr Zeiteintrag {id} wurde von der Verwaltung gelöscht.\n\n"
            f"Mit freundlichen Grüßen\n"
            f"Ihr TimeCare Pro-Team")
    send_email(email, subject, body)


@delete_time_entry_fv_blueprint.route('/delete_time_entry_fv/<int:zeiteintrags_id>', methods=['POST', 'GET'])
def delete_time_entry_fv(zeiteintrags_id):
    if request.method == 'POST':
        # übergebene ID und vermerk von welcher Funktion hierher geleitet
        origin_function = request.form.get('origin_function')
        booked = check_booked(zeiteintrags_id)
        email = get_email_by_zeiteintrag(zeiteintrags_id)
        lastname = get_lastname_by_email(email)
        # Zeiteintrag wurde schon gebucht
        if booked:
            error = ("Die Stundennachweise für diesen Monat wurden bereits gebucht."
                     " Der Eintrag kann nicht mehr gelöscht werden.")
            flash(error, 'error')
            redirect(url_for('delete_te'))

        else:
            # Löschen der Zeiteinträge und dazugehörigen Fahrten
            delete_zeiteintrag(zeiteintrags_id)
            send_email_delete_time_entry(email, lastname, zeiteintrags_id)
            # Erfolgsmeldung
            success_message = "Eintrag erfolgreich gelöscht."
            flash(success_message, 'success')

            # Rückleitungen zur Herkunftsfunktion
            return redirect(session.pop('url', None))

    return render_template('FV110_delete_time_entry_fv.html', zeiteintrags_id=zeiteintrags_id)
