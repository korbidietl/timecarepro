from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from db_query import (edit_zeiteintrag, delete_fahrt, add_fahrt, edit_fahrt,
                      fahrt_id_existing, check_for_overlapping_zeiteintrag, get_zeiteintrag_by_id,
                      get_fahrt_by_zeiteintrag, client_dropdown, get_email_by_zeiteintrag,
                      get_firstname_by_email, get_lastname_by_email, get_highest_fahrt_id, check_month_booked,
                      fahrt_ids_list)
from datetime import datetime
from email.mime.text import MIMEText
import smtplib
from FMOF030_create_time_entry import base64_to_blob

edit_time_entry_blueprint = Blueprint('edit_time_entry', __name__)


def check_time_entry_constraints(datum, start_zeit, end_zeit, klient_id):
    # Prüft ob, Startzeitpunkt vor Endzeitpunkt liegt.
    jetzt = datetime.now()
    if start_zeit >= end_zeit:
        flash("Endzeitpunkt muss nach Startzeitpunkt sein.")
        return True

    # prüft ob startzeitpunkt in der zukunft liegt
    if (start_zeit.time() > jetzt.time() and datum.date() > jetzt.date()) or datum.date() > jetzt.date():
        flash("Startzeitpunkt muss in der Vergangenheit liegen")
        return True

    # prüft ob dieser monat schon gebucht wurde
    datum.strftime("%m.%Y")
    if check_month_booked(datum, klient_id):
        flash("Die Stundennachweise für diesen Monat wurden bereits gebucht, es kann kein Eintrag mehr hinzugefügt "
              "werden")
        return True


@edit_time_entry_blueprint.route('/edit_time_entry/<int:zeiteintrag_id>', methods=['GET', 'POST'])
def edit_time_entry(zeiteintrag_id):
    # session speichern für rückleitung
    session_role = session.get('user_role')
    session['url_overlapping'] = url_for('edit_time_entry.edit_time_entry', zeiteintrag_id=zeiteintrag_id)
    return_url = session.get('url')

    # klienten für client_dropdown
    klienten = client_dropdown()

    highest_fahrt_id = get_highest_fahrt_id() + 1

    zeiteintrag_liste = get_zeiteintrag_by_id(zeiteintrag_id)
    zeiteintrag = zeiteintrag_liste[0]
    datum = zeiteintrag[3].strftime("%Y-%m-%d")
    von = zeiteintrag[3].strftime("%H:%M")
    bis = zeiteintrag[4].strftime("%H:%M")

    fahrten = get_fahrt_by_zeiteintrag(zeiteintrag_id)

    # Name Klient
    klient_id = zeiteintrag[6]

    if request.method == 'POST':
        # Eingabedaten aus dem Formular holen und in ein Dictionary speichern
        zeiteintrag_data = {
            'datum': request.form.get('datum'),
            'start_zeit': request.form.get('startZeit'),
            'end_zeit': request.form.get('endZeit'),
            'fachkraft': "1" if request.form.get('fachkraft') is not None else "0",
            'klient_id': request.form.get('klientDropdown'),
            'beschreibung': request.form.get('beschreibung'),
            'interne_notiz': request.form.get('interneNotiz'),
            'neue_unterschrift_klient': request.form.get('signatureDataKlient'),
            'neue_unterschrift_mitarbeiter': request.form.get('signatureDataMitarbeiter'),
            'absage': "1" if request.form.get('absage') is not None else "0"
        }

        # Überprüfung, ob alle notwendigen Felder ausgefüllt wurden
        if session_role != "Verwaltung":
            field_names = {
                'datum': "Das Datum",
                'startZeit': "Die Startzeit",
                'endZeit': "Die Endzeit",
                'klientDropdown': "Der Klient",
                'signatureDataMitarbeiter': "Die Mitarbeiterunterschrift"
            }
            for field in field_names:
                if not request.form.get(field):
                    flash(f'Es müssen alle Felder ausgefüllt werden. {field_names[field]} ist noch nicht ausgefüllt.')
                    return render_template("FMOF050_edit_time_entry.html", zeiteintrag=zeiteintrag, fahrten=fahrten,
                                           klient_id=klient_id, datum=datum, von=von, bis=bis,
                                           zeiteintrag_id=zeiteintrag_id, klienten=klienten, role=session_role,
                                           return_url=return_url)
        else:
            field_names = {
                'datum': "Das Datum",
                'startZeit': "Die Startzeit",
                'endZeit': "Die Endzeit",
                'klientDropdown': "Der Klient",
            }
            for field in field_names:
                if not request.form.get(field):
                    flash(f'Es müssen alle Felder ausgefüllt werden. {field_names[field]} ist noch nicht ausgefüllt.')
                    return render_template("FMOF050_edit_time_entry.html", zeiteintrag=zeiteintrag, fahrten=fahrten,
                                           klient_id=klient_id, datum=datum, von=von, bis=bis,
                                           zeiteintrag_id=zeiteintrag_id, klienten=klienten, role=session_role,
                                           return_url=return_url)

        # Konvertieren Sie die Datum- und Uhrzeitstrings in datetime-Objekte
        datum_datetime = datetime.strptime(zeiteintrag_data['datum'], '%Y-%m-%d')
        start_zeit_datetime = datetime.strptime(zeiteintrag_data['start_zeit'], '%H:%M').time()
        end_zeit_datetime = datetime.strptime(zeiteintrag_data['end_zeit'], '%H:%M').time()

        zeiteintrag_data['start_datetime'] = datetime.combine(datum_datetime, start_zeit_datetime)
        zeiteintrag_data['end_datetime'] = datetime.combine(datum_datetime, end_zeit_datetime)

        # Umwandeln der Unterschriften
        if zeiteintrag_data['neue_unterschrift_klient']:
            zeiteintrag_data['neue_unterschrift_klient'] = base64_to_blob(
                zeiteintrag_data['neue_unterschrift_klient'])
        if zeiteintrag_data['neue_unterschrift_mitarbeiter']:
            zeiteintrag_data['neue_unterschrift_mitarbeiter'] = base64_to_blob(
                zeiteintrag_data['neue_unterschrift_mitarbeiter'])

        zeiteintrag_data['mitarbeiter_id'] = zeiteintrag[5]

        # Überprüfen Sie, ob die Zeitbeschränkungen erfüllt sind
        if check_time_entry_constraints(datum_datetime, zeiteintrag_data['start_datetime'],
                                        zeiteintrag_data['end_datetime'], zeiteintrag_data['klient_id']):
            return render_template("FMOF050_edit_time_entry.html", zeiteintrag=zeiteintrag, fahrten=fahrten,
                                   klient_id=klient_id, datum=datum, von=von, bis=bis,
                                   zeiteintrag_id=zeiteintrag_id, klienten=klienten, role=session_role,
                                   highest_fahrt_id=highest_fahrt_id, return_url=return_url)


        fahrt_data_list = []
        form_data = request.form
        existing_fahrten_ids = get_fahrt_ids_from_form(form_data)

        for fahrt_id in existing_fahrten_ids:
            int_fahrtid = int(fahrt_id)

            kilometer = request.form.get(f'kilometer{int_fahrtid}', '').strip()
            start_adresse = request.form.get(f'start_adresse{int_fahrtid}', '').strip()
            end_adresse = request.form.get(f'end_adresse{int_fahrtid}', '').strip()

            if not kilometer and not start_adresse and not end_adresse:
                continue

            if kilometer is None or start_adresse is None or end_adresse is None:
                flash("Wenn eine Fahrt angelegt wird, müssen alle Felder ausgefüllt sein")
                break

            fahrt_data = {
                'fahrt_id': fahrt_id,
                'kilometer': kilometer,
                'start_adresse': start_adresse,
                'end_adresse': end_adresse,
                'abrechenbar': 1 if request.form.get(f'abrechenbarkeit{fahrt_id}') else 0,
                'zeiteintrag_id': zeiteintrag_id
            }
            fahrt_data_list.append(fahrt_data)

        if check_for_overlapping_zeiteintrag(zeiteintrag_id,
                                             zeiteintrag_data['start_datetime'], zeiteintrag_data['end_datetime']):
            session['overlapping_ze'] = zeiteintrag_data
            session['overlapping_fahrten'] = fahrt_data_list
            return redirect(
                url_for('check_overlapping_time.overlapping_time', zeiteintrag_id=zeiteintrag_id))

        # wenn kein overlapping dann trotzdem datenbank ausführen
        else:
            save_after_overlapping(zeiteintrag_id, zeiteintrag_data, fahrt_data_list)
            return redirect(url_for('client_hours_blueprint.client_supervision_hours', client_id=klient_id))

    return render_template("FMOF050_edit_time_entry.html", zeiteintrag=zeiteintrag, fahrten=fahrten,
                           klient_id=klient_id, datum=datum, von=von, bis=bis,
                           zeiteintrag_id=zeiteintrag_id, klienten=klienten, role=session_role,
                           highest_fahrt_id=highest_fahrt_id, return_url=return_url)


def save_after_overlapping(zeiteintrag_id, zeiteintrag_data, fahrt_data_list):
    session_role = session.get('user_role')
    klient_id = zeiteintrag_data['klient_id']
    # zeiteintrag dictionary extrahieren

    edit_zeiteintrag(zeiteintrag_id, zeiteintrag_data['start_datetime'], zeiteintrag_data['end_datetime'],
                     zeiteintrag_data['neue_unterschrift_mitarbeiter'], zeiteintrag_data['neue_unterschrift_klient'],
                     zeiteintrag_data['klient_id'], zeiteintrag_data['fachkraft'], zeiteintrag_data['beschreibung'],
                     zeiteintrag_data['interne_notiz'], zeiteintrag_data['absage'])

    # wenn verwaltung ändert, muss E-Mail an mitarbeiter gesendet werden
    added_fahrten = []
    if session_role == "Verwaltung":
        email = get_email_by_zeiteintrag(zeiteintrag_id)
        firstname = get_firstname_by_email(email)
        lastname = get_lastname_by_email(email)
        send_email_edit_time_entry(email, firstname, lastname, zeiteintrag_id)

    else:
        for fahrt_data in fahrt_data_list:
            if fahrt_id_existing(fahrt_data['fahrt_id']):
                # Aktualisiere die bestehende Fahrt
                edit_fahrt(fahrt_data['fahrt_id'], fahrt_data['kilometer'], fahrt_data['abrechenbar'],
                           fahrt_data['zeiteintrag_id'], fahrt_data['start_adresse'],
                           fahrt_data['end_adresse'], )
                added_fahrten.append(fahrt_data['fahrt_id'])
            else:
                # Füge neue Fahrt hinzu
                fahrten = add_fahrt(fahrt_data['kilometer'], fahrt_data['start_adresse'], fahrt_data['end_adresse'],
                                    fahrt_data['abrechenbar'], fahrt_data['zeiteintrag_id'])
                added_fahrten.append(str(fahrten))

            # Lösche entfernte Fahrten
        fahrt_ids = fahrt_ids_list(zeiteintrag_id)
        for fahrt_id in fahrt_ids:
            found = False
            for fahrt_data in added_fahrten:
                if str(fahrt_id) == fahrt_data:
                    found = True
                    break
            if not found:
                delete_fahrt(fahrt_id)

    flash('Eintrag erfolgreich gespeichert')
    return redirect(url_for('client_hours_blueprint.client_supervision_hours', client_id=klient_id))


def send_email(email, subject, body):
    msg = MIMEText(body)

    msg['Subject'] = subject
    msg['From'] = 'edittimeentry@timecarepro.de'
    msg['To'] = email

    with smtplib.SMTP('132.231.36.210', 1103) as smtp:
        smtp.login('mailhog_grup3', 'Uni75Winfo17Master')
        smtp.sendmail('resetyourpassword@timecarepro.de', [email], msg.as_string())


def send_email_edit_time_entry(email, firstname, lastname, z_id):
    subject = "Bearbeiteter Zeiteintrag"
    body = (f"Sehr geehrte/r {firstname} {lastname}, \n\n"
            f"Ihr Zeiteintrag {z_id} wurde von der Verwaltung bearbeitet.\n"
            f"Bitte prüfen und unterschreiben Sie den geänderten Eintrag.\n\n"
            f"Freundliche Grüße\n"
            f"Ihr TimeCare Pro-Team")
    send_email(email, subject, body)


def get_fahrt_ids_from_form(form_data):
    fahrt_ids = []
    for key in form_data.keys():
        if key.startswith('fahrt_id'):
            # Fügt die Werte der Formularelemente hinzu, die mit 'fahrt_id' beginnen
            fahrt_ids.append(form_data[key])
    return fahrt_ids
