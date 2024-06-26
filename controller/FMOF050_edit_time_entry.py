import os
from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from model.buchung import check_month_booked
from model.mailserver_connection import send_email
from model.person import get_firstname_by_email, get_lastname_by_email
from model.klient import client_dropdown
from model.fahrt import add_fahrt, get_fahrt_by_zeiteintrag, edit_fahrt, delete_fahrt, get_highest_fahrt_id, \
    fahrt_id_existing, fahrt_ids_list
from model.zeiteintrag import check_for_overlapping_zeiteintrag, get_zeiteintrag_by_id, edit_zeiteintrag, \
    get_email_by_zeiteintrag, delete_zeiteintrag
from datetime import datetime
from controller.FMOF030_create_time_entry import base64_to_blob

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
    if 'user_id' in session:
        user_role = session['user_role']
        person_id = session['user_id']
        ueberschneidung = session['ueberschneidung']
        if user_role == 'Steuerbüro' or user_role == 'Sachbearbeiter/Kostenträger':
            flash('Sie sind nicht berechtigt diese Seite aufzurufen.')
            return redirect(session['secure_url'])
        else:
            # Rückleitung bei unerlaubter Seite
            session['secure_url'] = url_for('edit_time_entry.edit_time_entry', zeiteintrag_id=zeiteintrag_id)

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
                    'absage': "1" if request.form.get('absage') is not None else "0",
                    'zeiteintrag_id': zeiteintrag_id
                }

                ze_signatures = {
                    'neue_unterschrift_klient': request.form.get('signatureDataKlient'),
                    'neue_unterschrift_mitarbeiter': request.form.get('signatureDataMitarbeiter')
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

                    if session['ueberschneidung'] != 1:
                        for field in field_names:
                            if not request.form.get(field):
                                flash(f'Es müssen alle Felder ausgefüllt werden. '
                                      f'{field_names[field]} ist noch nicht ausgefüllt.')
                                return render_template("FMOF050_edit_time_entry.html", zeiteintrag=zeiteintrag,
                                                       fahrten=fahrten, klient_id=klient_id, datum=datum, von=von,
                                                       bis=bis, zeiteintrag_id=zeiteintrag_id, klienten=klienten,
                                                       role=session_role, return_url=return_url,
                                                       highest_fahrt_id=highest_fahrt_id, person_id=person_id,
                                                       ueberschneidung=ueberschneidung)
                else:
                    field_names = {
                        'datum': "Das Datum",
                        'startZeit': "Die Startzeit",
                        'endZeit': "Die Endzeit",
                        'klientDropdown': "Der Klient",
                    }
                    for field in field_names:
                        if not request.form.get(field):
                            flash(f'Es müssen alle Felder ausgefüllt werden. '
                                  f'{field_names[field]} ist noch nicht ausgefüllt.')
                            return render_template("FMOF050_edit_time_entry.html", zeiteintrag=zeiteintrag,
                                                   fahrten=fahrten, klient_id=klient_id, datum=datum, von=von, bis=bis,
                                                   zeiteintrag_id=zeiteintrag_id, klienten=klienten, role=session_role,
                                                   return_url=return_url, highest_fahrt_id=highest_fahrt_id,
                                                   person_id=person_id, ueberschneidung=ueberschneidung)

                # Konvertieren Sie die Datum- und Uhrzeitstrings in datetime-Objekte
                datum_datetime = datetime.strptime(zeiteintrag_data['datum'], '%Y-%m-%d')
                start_zeit_datetime = datetime.strptime(zeiteintrag_data['start_zeit'], '%H:%M').time()
                end_zeit_datetime = datetime.strptime(zeiteintrag_data['end_zeit'], '%H:%M').time()

                zeiteintrag_data['start_datetime'] = datetime.combine(datum_datetime, start_zeit_datetime)
                zeiteintrag_data['end_datetime'] = datetime.combine(datum_datetime, end_zeit_datetime)

                signatures_path = {}

                # Umwandeln der Unterschriften
                if ze_signatures['neue_unterschrift_klient']:
                    blob = base64_to_blob(ze_signatures['neue_unterschrift_klient'])
                    path = 'path/to/storage/klient_signature.bin'
                    signatures_path['neue_unterschrift_klient'] = save_blob(blob, path)

                if ze_signatures['neue_unterschrift_mitarbeiter']:
                    blob = base64_to_blob(ze_signatures['neue_unterschrift_mitarbeiter'])
                    path = 'path/to/storage/mitarbeiter_signature.bin'
                    signatures_path['neue_unterschrift_mitarbeiter'] = save_blob(blob, path)

                zeiteintrag_data['mitarbeiter_id'] = zeiteintrag[5]

                # Überprüfen, ob die Zeitbeschränkungen erfüllt sind
                if check_time_entry_constraints(datum_datetime, zeiteintrag_data['start_datetime'],
                                                zeiteintrag_data['end_datetime'], zeiteintrag_data['klient_id']):
                    return render_template("FMOF050_edit_time_entry.html", zeiteintrag=zeiteintrag, fahrten=fahrten,
                                           klient_id=klient_id, datum=datum, von=von, bis=bis,
                                           zeiteintrag_id=zeiteintrag_id, klienten=klienten, role=session_role,
                                           highest_fahrt_id=highest_fahrt_id, return_url=return_url,
                                           person_id=person_id, ueberschneidung=ueberschneidung)

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

                if check_for_overlapping_zeiteintrag(zeiteintrag_id, zeiteintrag_data['start_datetime'],
                                                     zeiteintrag_data['end_datetime']):
                    session['ueberschneidung'] = 1
                    zeiteintrag_data['zeiteintrag_id'] = zeiteintrag_id
                    session['overlapping_ze'] = zeiteintrag_data
                    session['ze_signatures'] = signatures_path
                    session['overlapping_fahrten'] = fahrt_data_list
                    return redirect(
                        url_for('check_overlapping_time.overlapping_time', zeiteintrag_id=zeiteintrag_id))

                # wenn kein overlapping dann trotzdem datenbank ausführen
                else:
                    session['ueberschneidung'] = 0
                    save_after_overlapping(zeiteintrag_id, zeiteintrag_data, fahrt_data_list, signatures_path)
                    return redirect(return_url)

            return render_template("FMOF050_edit_time_entry.html", zeiteintrag=zeiteintrag, fahrten=fahrten,
                                   klient_id=klient_id, datum=datum, von=von, bis=bis,
                                   zeiteintrag_id=zeiteintrag_id, klienten=klienten, role=session_role,
                                   highest_fahrt_id=highest_fahrt_id, return_url=return_url, person_id=person_id,
                                   ueberschneidung=ueberschneidung)

    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))


def save_after_overlapping(zeiteintrag_id, zeiteintrag_data, fahrt_data_list, ze_signatures):
    session_role = session.get('user_role')
    klient_id = zeiteintrag_data['klient_id']
    signature_mitarbeiter = load_blob(ze_signatures['neue_unterschrift_mitarbeiter'])
    neue_unterschrift_klient = ze_signatures.get('neue_unterschrift_klient', None)
    if neue_unterschrift_klient:
        signature_klient = load_blob(ze_signatures['neue_unterschrift_klient'])
    else:
        signature_klient = None
    # zeiteintrag dictionary extrahieren
    edit_zeiteintrag(zeiteintrag_id, zeiteintrag_data['start_datetime'], zeiteintrag_data['end_datetime'],
                     signature_mitarbeiter, signature_klient,
                     zeiteintrag_data['klient_id'], zeiteintrag_data['fachkraft'], zeiteintrag_data['beschreibung'],
                     zeiteintrag_data['interne_notiz'], zeiteintrag_data['absage'])

    # wenn verwaltung ändert, muss E-Mail an mitarbeiter gesendet werden
    added_fahrten = []
    if session_role == "Verwaltung" or session_role == "Geschäftsführung":
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


def send_email_edit_time_entry(email, firstname, lastname, z_id):
    subject = "Bearbeiteter Zeiteintrag"
    role = session['user_role']
    body = (f"Sehr geehrte/r {firstname} {lastname}, \n\n"
            f"Ihr Zeiteintrag {z_id} wurde von einem Mitarbeiter der {role} bearbeitet.\n"
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


def save_blob(blob, path):
    # Überprüfen, ob das Verzeichnis existiert, und wenn nicht, erstellen
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(path, 'wb') as file:
        file.write(blob)
    return path


def load_blob(path):
    with open(path, 'rb') as file:
        blob = file.read()
    return blob


delete_if_ueberschneidung_blueprint = Blueprint('delete_if_ueberschneidung', __name__)


@delete_if_ueberschneidung_blueprint.route('/delete/<int:zeiteintrag_id>', methods=['POST'])
def delete_if_ueberschneidung(zeiteintrag_id):
    if request.method == 'POST':
        zeiteintrag_data = get_zeiteintrag_by_id(zeiteintrag_id)
        klient_id = zeiteintrag_data[0][6]
        delete_zeiteintrag(zeiteintrag_id)
        session['ueberschneidung'] = 0
        return redirect(url_for('client_hours_blueprint.client_supervision_hours', client_id=klient_id))
