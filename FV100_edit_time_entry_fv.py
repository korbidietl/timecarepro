import smtplib
from datetime import datetime
from email.mime.text import MIMEText

from flask import Blueprint, request, render_template, redirect, url_for, flash
from db_query import get_zeiteintrag_with_fahrten_by_id, edit_zeiteintrag, get_email_by_zeiteintrag, \
    get_lastname_by_email

edit_time_entry_fv_blueprint = Blueprint('edit_time_entry_fv', __name__)


def send_email(email, subject, body):
    msg = MIMEText(body)

    msg['Subject'] = subject
    msg['From'] = 'deletetimeentry@timecarepro.de'
    msg['To'] = email

    with smtplib.SMTP('132.231.36.210', 1103) as smtp:
        smtp.starttls()
    smtp.login('mailhog_grup3', 'Uni75Winfo17Master')
    smtp.sendmail('edittimeentry@timecarepro.de', [email], msg.as_string())


def send_email_edit_time_entry(email, lastname, id):
    subject = "Bearbeiteter Zeiteintrag"
    body = (f"Sehr geehrte/r Frau/Mann {lastname}, \n\n"
            f"Ihr Zeiteintrag {id} wurde von der Verwaltung bearbeitet."
            f"Bitte prüfen und unterschreiben Sie den geänderten Eintrag.\n\n"
            f"Mit freundlichen Grüßen\n"
            f"Ihr TimeCare Pro-Team")
    send_email(email, subject, body)


@edit_time_entry_fv_blueprint.route('/edit_time_entry_fv/<int:zeiteintrag_id>', methods=['GET', 'POST'])
def edit_time_entry(zeiteintrag_id):
    email = get_email_by_zeiteintrag(zeiteintrag_id)
    lastname = get_lastname_by_email(email)
    if request.method == 'GET':
        # Daten für den zu bearbeitenden Zeiteintrag holen
        zeiteintrag_data = get_zeiteintrag_with_fahrten_by_id(zeiteintrag_id)
        return render_template("FV100_edit_time_entry_fv.html",
                               zeiteintrag=zeiteintrag_data['zeiteintrag'], zeiteintrag_id=zeiteintrag_id)
    else:
        # Eingabedaten aus dem Formular holen
        datum = request.form.get('datum')
        start_zeit = request.form.get('startZeit')
        end_zeit = request.form.get('endZeit')
        fachkraft = request.form.get('fachkraft')
        klient_id = request.form.get('klient')
        beschreibung = request.form.get('beschreibung')
        interne_notiz = request.form.get('interneNotiz')
        absage = request.form.get('absage')

        # Konvertiere Datum und Uhrzeit in ein datetime-Objekt
        start_datetime = datetime.strptime(f"{datum} {start_zeit}", '%Y-%m-%d %H:%M')
        end_datetime = datetime.strptime(f"{datum} {end_zeit}", '%Y-%m-%d %H:%M')

        # Änderungen am Zeiteintrag speichern
        edit_zeiteintrag(zeiteintrag_id, start_datetime, end_datetime, klient_id, fachkraft,
                         beschreibung, interne_notiz, absage)
        send_email_edit_time_entry(email, lastname, zeiteintrag_id)
        # Erfolgsmeldung
        success_message = "Eintrag erfolgreich bearbeitet."
        flash(success_message, 'success')
        # Weiterleitung zurück zur Übersicht der abgelegten Stunden
        return redirect(url_for('/FMOF010_show_supervisionhours_client'))
