import smtplib
from email.mime.text import MIMEText

from flask import Blueprint, request, flash, redirect, url_for, render_template, session
from db_query import delete_zeiteintrag, check_booked, get_email_by_zeiteintrag, get_firstname_by_email, \
    get_lastname_by_email

delete_time_entry_blueprint = Blueprint("delete_te", __name__)


@delete_time_entry_blueprint.route('/delete_te/<int:zeiteintrags_id>', methods=['POST', 'GET'])
def delete_te(zeiteintrags_id):
    return_url = session.get('url')
    session_role = session.get('user_role')
    if request.method == 'POST':
        # Zeiteintrag wurde schon gebucht
        if check_booked(zeiteintrags_id):
            error = ("Die Stundennachweise für diesen Monat wurden bereits gebucht."
                     " Der Eintrag kann nicht mehr gelöscht werden.")
            flash(error, 'error')
            render_template('FMOF060_delete_time_entry.html', zeiteintrags_id=zeiteintrags_id)

        else:
            # Löschen der Zeiteinträge und dazugehörigen Fahrten
            delete_zeiteintrag(zeiteintrags_id)
            # wenn rolle verwaltung löscht, muss E-Mail gesendet werden
            if session_role == "Verwaltung":
                email = get_email_by_zeiteintrag(zeiteintrags_id)
                firstname = get_firstname_by_email(email)
                lastname = get_lastname_by_email(email)
                send_email_delete_time_entry(email, firstname, lastname, zeiteintrags_id)
            # Erfolgsmeldung
            success_message = "Eintrag erfolgreich gelöscht."
            flash(success_message, 'success')

            # Rückleitungen zur Herkunftsfunktion und löschen aus der Session
            return redirect(session.pop('url', None))
    return render_template('FMOF060_delete_time_entry.html', zeiteintrags_id=zeiteintrags_id, return_url=return_url)


def send_email(email, subject, body):
    msg = MIMEText(body)

    msg['Subject'] = subject
    msg['From'] = 'deletetimeentry@timecarepro.de'
    msg['To'] = email

    with smtplib.SMTP('132.231.36.210', 1103) as smtp:
        smtp.login('mailhog_grup3', 'Uni75Winfo17Master')
        smtp.sendmail('deletetimeentry@timecarepro.de', [email], msg.as_string())


def send_email_delete_time_entry(email, firstname, lastname, zeiteintrag_id):
    subject = "Gelöschter Zeiteintrag"
    body = (f"Sehr geehrte/r {firstname} {lastname}, \n\n"
            f"Ihr Zeiteintrag {zeiteintrag_id} wurde von der Verwaltung gelöscht.\n\n"
            f"Freundliche Grüße\n"
            f"Ihr TimeCare Pro-Team")
    send_email(email, subject, body)
