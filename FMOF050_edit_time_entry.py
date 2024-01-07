from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from db_query import (edit_zeiteintrag, delete_fahrt, add_fahrt, edit_fahrt,
                      fahrt_id_existing, check_for_overlapping_zeiteintrag, get_zeiteintrag_by_id,
                      get_fahrt_by_zeiteintrag, get_klient_data, client_dropdown, get_email_by_zeiteintrag,
                      get_firstname_by_email, get_lastname_by_email)
from datetime import datetime
from email.mime.text import MIMEText
import smtplib
from FMOF030_create_time_entry import check_time_entry_constraints, base64_to_blob

edit_time_entry_blueprint = Blueprint('edit_time_entry', __name__)


@edit_time_entry_blueprint.route('/edit_time_entry/<int:zeiteintrag_id>', methods=['GET', 'POST'])
def edit_time_entry(zeiteintrag_id):
    # session speichern für rückleitung
    session_role = session.get('user_role')
    session['url_overlapping'] = url_for('edit_time_entry.edit_time_entry', zeiteintrag_id=zeiteintrag_id)

    # klienten für client_dropdown
    klienten = client_dropdown()

    zeiteintrag_liste = get_zeiteintrag_by_id(zeiteintrag_id)
    zeiteintrag = zeiteintrag_liste[0]
    datum = zeiteintrag[3].strftime("%Y-%m-%d")
    von = zeiteintrag[3].strftime("%H:%M")
    bis = zeiteintrag[4].strftime("%H:%M")

    fahrten = get_fahrt_by_zeiteintrag(zeiteintrag_id)

    # Name Klient
    klient_id = zeiteintrag[6]

    print(klient_id)
    print(session_role)
    if request.method == 'POST':
        # Eingabedaten aus dem Formular holen
        datum = request.form.get('datum')
        start_zeit = request.form.get('startZeit')
        end_zeit = request.form.get('endZeit')
        fachkraft = request.form.get('fachkraft')
        klient_id = request.form.get('klientDropdown')
        beschreibung = request.form.get('beschreibung')
        interne_notiz = request.form.get('interneNotiz')
        neue_unterschrift_klient = request.form.get('signatureDataKlient')
        neue_unterschrift_mitarbeiter = request.form.get('signatureDataMitarbeiter')
        absage = "1" if request.form.get('absage') is not None else "0"

        # Konvertiere Datum und Uhrzeit in ein datetime-Objekt
        datum_datetime = datetime.strptime(datum, '%Y-%m-%d')
        start_zeit_datetime = datetime.strptime(start_zeit, '%H:%M').time()
        end_zeit_datetime = datetime.strptime(end_zeit, '%H:%M').time()

        start_datetime = datetime.combine(datum_datetime, start_zeit_datetime)
        end_datetime = datetime.combine(datum_datetime, end_zeit_datetime)

        if not check_time_entry_constraints(datum_datetime, start_datetime, end_datetime, klient_id):
            # Umwandlung der Unterschriften
            if neue_unterschrift_klient:
                neue_unterschrift_klient = base64_to_blob(neue_unterschrift_klient)
            if neue_unterschrift_mitarbeiter:
                neue_unterschrift_mitarbeiter = base64_to_blob(neue_unterschrift_mitarbeiter)

            # Änderungen am Zeiteintrag speichern
            edit_zeiteintrag(zeiteintrag_id, start_datetime, end_datetime,neue_unterschrift_mitarbeiter, neue_unterschrift_klient,
                              klient_id, fachkraft, beschreibung, interne_notiz, absage)

            if check_for_overlapping_zeiteintrag(zeiteintrag_id, klient_id, start_datetime, end_datetime):
                return redirect(url_for('/check_overlapping_time', zeiteintrag_id=zeiteintrag_id))

            # wenn verwaltung ändert, muss E-Mail an mitarbeiter gesendet werden
            if session_role == "Verwaltung":
                email = get_email_by_zeiteintrag(zeiteintrag_id)
                firstname = get_firstname_by_email(email)
                lastname = get_lastname_by_email(email)
                send_email_edit_time_entry(email, firstname, lastname, zeiteintrag_id)

                flash('Eintrag erfolgreich bearbeitet')
                return redirect(session.pop('url', None))

        else:
            check_time_entry_constraints(datum_datetime, start_datetime, end_datetime, klient_id)

        # verwaltung kann nur tabelle zeiteintrag ändern nicht aber fahrten (laut pflichtenheft!!)
        if not session_role == "Verwaltung":
            # importiere fahrtCounter von html hidden input in python
            fahrtCounter = int(request.form.get('fahrtCounterInput', 1))

            # Bearbeite Fahrt-Einträge
            existing_fahrten_ids = request.form.getlist('existing_fahrten_ids')

            for fahrt_id in existing_fahrten_ids:
                kilometer = request.form[f'kilometer{fahrt_id}']
                start_adresse = request.form[f'start_adresse{fahrt_id}']
                end_adresse = request.form[f'end_adresse{fahrt_id}']
                if not (kilometer is None and start_adresse is None and end_adresse is None):
                    if kilometer is None or start_adresse is None or end_adresse is None:
                        flash("Wenn eine Fahrt angelegt wird müssen alle Felder ausgefüllt sein")
                        break

                # aktualisiere die Fahrt
                edit_fahrt(fahrt_id=request.form[f'fahrt_id{fahrt_id}'], kilometer=request.form[f'kilometer{fahrt_id}'],
                           abrechenbar=request.form.get(f'abrechenbarkeit{fahrt_id}', False),
                           start_adresse=request.form[f'start_adresse{fahrt_id}'],
                           end_adresse=request.form[f'end_adresse{fahrt_id}'],
                           zeiteintrag_id=zeiteintrag_id)

            # Füge neue Fahrten hinzu
            for i in range(fahrtCounter):  # fahrtCounter sollte vom Frontend übergeben werden
                if not f'fahrt_id{i}':
                    add_fahrt(kilometer=request.form[f'kilometer_new{i}'],
                              start_adresse=request.form[f'start_adresse_new{i}'],
                              end_adresse=request.form[f'end_adresse_new{i}'],
                              abrechenbar=request.form.get(f'abrechenbarkeit_new{i}', False),
                              zeiteintrag_id=zeiteintrag_id)

            # fahrt entfernen
            # wenn fahrt id nicht mehr in bestehenden fahrten ist, dann löschen
            for i in range(fahrtCounter):
                if not fahrt_id_existing(f'fahrt_id{i}'):
                    delete_fahrt(f'fahrt_id{i}')

            # Weiterleitung zurück zur Übersicht der abgelegten Stunden
            flash('Eintrag erfolgreich bearbeitet')
            return redirect(session.pop('url', None))

    return render_template("FMOF050_edit_time_entry.html", zeiteintrag=zeiteintrag, fahrten=fahrten,
                           klient_id=klient_id, datum=datum, von=von, bis=bis,
                           zeiteintrag_id=zeiteintrag_id, klienten=klienten, role=session_role)


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
