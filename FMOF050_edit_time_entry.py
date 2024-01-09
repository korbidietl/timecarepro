from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from db_query import (edit_zeiteintrag, delete_fahrt, add_fahrt, edit_fahrt,
                      fahrt_id_existing, check_for_overlapping_zeiteintrag, get_zeiteintrag_by_id,
                      get_fahrt_by_zeiteintrag, client_dropdown, get_email_by_zeiteintrag,
                      get_firstname_by_email, get_lastname_by_email, get_highest_fahrt_id)
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
    return_url = session.get('url')

    # klienten für client_dropdown
    klienten = client_dropdown()

    highest_fahrt_id = get_highest_fahrt_id()
    print("höchste fahrt:", highest_fahrt_id)

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

        # Überprüfung ob alle notwendigen Felder ausgefüllt wurden
        field_names = {
            'datum': "Das Datum",
            'startZeit': "Die Startzeit",
            'endZeit': "Die Endzeit",
            'klientDropdown': "Der Klient",
            'signatureDataMitarbeiter': "Die Mitarbeiterunterschrift"
        }

        # Überprüfung, ob alle notwendigen Felder ausgefüllt wurden
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

        # Überprüfen Sie, ob die Zeitbeschränkungen erfüllt sind
        if check_time_entry_constraints(datum_datetime, zeiteintrag_data['start_datetime'],
                                        zeiteintrag_data['end_datetime'], zeiteintrag_data['klient_id']):
            return render_template("FMOF050_edit_time_entry.html", zeiteintrag=zeiteintrag, fahrten=fahrten,
                                   klient_id=klient_id, datum=datum, von=von, bis=bis,
                                   zeiteintrag_id=zeiteintrag_id, klienten=klienten, role=session_role,
                                   highest_fahrt_id=highest_fahrt_id, return_url=return_url)

        # verwaltung kann nur tabelle zeiteintrag ändern nicht aber fahrten (laut pflichtenheft!!)
        if not session_role == "Verwaltung":

            # Bearbeite Fahrt-Einträge
            existing_fahrten_ids = request.form.getlist('fahrt_id')

            for fahrt_id in existing_fahrten_ids:
                kilometer = request.form[f'kilometer{fahrt_id}']
                start_adresse = request.form[f'start_adresse{fahrt_id}']
                end_adresse = request.form[f'end_adresse{fahrt_id}']
                if not (kilometer is None and start_adresse is None and end_adresse is None):
                    if kilometer is None or start_adresse is None or end_adresse is None:
                        flash("Wenn eine Fahrt angelegt wird müssen alle Felder ausgefüllt sein")
                        break

        fahrt_data_list = []

        if session_role != "Verwaltung":
            print("fahrt einlesen")
            fahrt_data_list = []
            # existing_fahrten_ids = request.form.getlist('fahrt_id')
            form_data = request.form
            existing_fahrten_ids = get_fahrt_ids_from_form(form_data)
            print(existing_fahrten_ids)

            for fahrt_id in existing_fahrten_ids:
                int_fahrtid = int(fahrt_id)
                newFahrtID = int_fahrtid + highest_fahrt_id
                print("fahrt id:", fahrt_id)
                print("fahrt id:", int_fahrtid)
                print("highest fahrt:", highest_fahrt_id)
                print("new fahrt:", newFahrtID)
                kilometer = request.form[f'kilometer{newFahrtID}']
                start_adresse = request.form[f'start_adresse{newFahrtID}']
                end_adresse = request.form[f'end_adresse{fahrt_id}']
                if kilometer is None or start_adresse is None or end_adresse is None:
                    flash("Wenn eine Fahrt angelegt wird, müssen alle Felder ausgefüllt sein")
                    break

                fahrt_data = {
                    'fahrt_id': fahrt_id,
                    'kilometer': kilometer,
                    'start_adresse': start_adresse,
                    'end_adresse': end_adresse,
                    'abrechenbar': request.form.get(f'abrechenbarkeit{fahrt_id}', False),
                    'zeiteintrag_id': zeiteintrag_id
                }
                fahrt_data_list.append(fahrt_data)

        print(6)
        print(check_for_overlapping_zeiteintrag(zeiteintrag_id, zeiteintrag_data['datum'],
                                                zeiteintrag_data['start_datetime'], zeiteintrag_data['end_datetime']))

        if check_for_overlapping_zeiteintrag(zeiteintrag_id, zeiteintrag_data['datum'],
                                             zeiteintrag_data['start_datetime'], zeiteintrag_data['end_datetime']):
            print("überschneidung")
            return redirect(
                url_for('check_overlapping_time.overlapping_time', zeiteintrag_id=zeiteintrag_id,
                        zeiteintrag_data=zeiteintrag_data, fahrt_data_list=fahrt_data_list))

        # wenn kein overlapping dann trotzdem datenbank ausführen
        else:
            save_after_overlapping(zeiteintrag_id, zeiteintrag_data, fahrt_data_list)

    return render_template("FMOF050_edit_time_entry.html", zeiteintrag=zeiteintrag, fahrten=fahrten,
                           klient_id=klient_id, datum=datum, von=von, bis=bis,
                           zeiteintrag_id=zeiteintrag_id, klienten=klienten, role=session_role,
                           highest_fahrt_id=highest_fahrt_id, return_url=return_url)


def save_after_overlapping(zeiteintrag_id, zeiteintrag_data, fahrt_data_list):
    session_role = session.get('user_role')
    klient_id = zeiteintrag_data['klient_id']
    # zeiteintrag dictionary extrahieren
    print(7)

    edit_zeiteintrag(zeiteintrag_id, zeiteintrag_data['start_datetime'], zeiteintrag_data['end_datetime'],
                     zeiteintrag_data['neue_unterschrift_mitarbeiter'], zeiteintrag_data['neue_unterschrift_klient'],
                     zeiteintrag_data['klient_id'], zeiteintrag_data['fachkraft'], zeiteintrag_data['beschreibung'],
                     zeiteintrag_data['interne_notiz'], zeiteintrag_data['absage'])

    # wenn verwaltung ändert, muss E-Mail an mitarbeiter gesendet werden
    print(session_role)
    print(fahrt_data_list)
    if session_role == "Verwaltung":
        print("verwaltung")
        email = get_email_by_zeiteintrag(zeiteintrag_id)
        firstname = get_firstname_by_email(email)
        lastname = get_lastname_by_email(email)
        send_email_edit_time_entry(email, firstname, lastname, zeiteintrag_id)

    else:
        for fahrt_data in fahrt_data_list:
            print("fahrt")
            print(fahrt_id_existing(fahrt_data['fahrt_id']))
            if fahrt_id_existing(fahrt_data['fahrt_id']):
                print(fahrt_data['fahrt_id'])
                # Aktualisiere die bestehende Fahrt
                edit_fahrt(fahrt_data['fahrt_id'], fahrt_data['kilometer'], fahrt_data['abrechenbar'],
                           fahrt_data['zeiteintrag_id'], fahrt_data['start_adresse'], fahrt_data['end_adresse'], )
            else:
                # Füge neue Fahrt hinzu
                add_fahrt(fahrt_data['kilometer'], fahrt_data['start_adresse'], fahrt_data['end_adresse'],
                          fahrt_data['abrechenbar'], fahrt_data['zeiteintrag_id'])

            # Lösche entfernte Fahrten
        for fahrt_data in fahrt_data_list:
            if not fahrt_id_existing(fahrt_data['fahrt_id']):
                delete_fahrt(fahrt_data['fahrt_id'])

    flash('Eintrag erfolgreich gespeichert')
    return redirect(url_for('client_hours_blueprint.client_supervision_hours', client_id=klient_id))


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


def get_fahrt_ids_from_form(form_data):
    fahrt_ids = []
    for key in form_data.keys():
        if key.startswith('fahrt_id'):
            # Fügt die Werte der Formularelemente hinzu, die mit 'fahrt_id' beginnen
            fahrt_ids.append(form_data[key])
    return fahrt_ids
