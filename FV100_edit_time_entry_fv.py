import base64
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from db_query import edit_zeiteintrag, get_email_by_zeiteintrag, \
    get_lastname_by_email, check_for_overlapping_zeiteintrag, get_zeiteintrag_by_id, get_fahrt_by_zeiteintrag, \
    get_klient_data, get_firstname_by_email

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


def send_email_edit_time_entry(email, firstname, lastname, z_id):
    subject = "Bearbeiteter Zeiteintrag"
    body = (f"Sehr geehrte/r {firstname} {lastname}, \n\n"
            f"Ihr Zeiteintrag {z_id} wurde von der Verwaltung bearbeitet."
            f"Bitte prüfen und unterschreiben Sie den geänderten Eintrag.\n\n"
            f"Freundliche Grüße\n"
            f"Ihr TimeCare Pro-Team")
    send_email(email, subject, body)


@edit_time_entry_fv_blueprint.route('/edit_time_entry_fv/<int:zeiteintrag_id>', methods=['GET', 'POST'])
def edit_time_entry(zeiteintrag_id):
    session['url_overlapping'] = url_for('edit_time_entry_fv.edit_time_entry', zeiteintrag_id=zeiteintrag_id)
    email = get_email_by_zeiteintrag(zeiteintrag_id)
    firstname = get_firstname_by_email(email)
    lastname = get_lastname_by_email(email)

    zeiteintrag_liste = get_zeiteintrag_by_id(zeiteintrag_id)
    zeiteintrag = zeiteintrag_liste[0]
    datum = zeiteintrag[3].strftime("%Y-%m-%d")
    von = zeiteintrag[3].strftime("%H:%M")
    bis = zeiteintrag[4].strftime("%H:%M")

    fahrten = get_fahrt_by_zeiteintrag(zeiteintrag_id)

    # Name Klient
    klient_id = zeiteintrag[6]
    klient_data = get_klient_data(klient_id)
    klient_name = klient_data[0][1] + ' ' + klient_data[0][2]

    # Umwandlung Unterschriften
    if zeiteintrag[1]:
        unterschrift_mitarbeiter = base64.b64encode(zeiteintrag[1]).decode('utf-8')
    else:
        unterschrift_mitarbeiter = ""

    if zeiteintrag[2]:
        unterschrift_klient = base64.b64encode(zeiteintrag[2]).decode('utf-8')
    else:
        unterschrift_klient = ""

    if request.method == 'POST':
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

        if check_for_overlapping_zeiteintrag(zeiteintrag_id, start_datetime, end_datetime):
            return redirect(url_for('/check_overlapping_time', zeiteintrag_id=zeiteintrag_id))

        send_email_edit_time_entry(email, firstname, lastname, zeiteintrag_id)
        # Erfolgsmeldung
        success_message = "Eintrag erfolgreich bearbeitet."
        flash(success_message, 'success')
        # Weiterleitung zurück zur Übersicht der abgelegten Stunden
        return redirect(url_for('/FMOF010_show_supervisionhours_client'))

    return render_template("FV100_edit_time_entry_fv.html",
                           zeiteintrag=zeiteintrag, fahrten=fahrten,
                           klient_name=klient_name, datum=datum, von=von, bis=bis,
                           unterschrift_klient=unterschrift_klient,
                           unterschrift_mitarbeiter=unterschrift_mitarbeiter, zeiteintrag_id=zeiteintrag_id)
