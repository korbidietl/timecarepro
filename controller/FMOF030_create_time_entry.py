import base64
import os

from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from model.buchung import check_month_booked
from model.klient import client_dropdown, get_klient_data
from model.fahrt import add_fahrt
from model.zeiteintrag import check_for_overlapping_zeiteintrag, add_zeiteintrag
from datetime import datetime

create_time_entry_blueprint = Blueprint('/create_time_entry', __name__)


def check_time_entry_constraints(datum, start_zeit, end_zeit, klient_id, person_id):
    # Prüft ob, Startzeitpunkt vor Endzeitpunkt liegt.
    jetzt = datetime.now()
    if start_zeit >= end_zeit:
        flash("Endzeitpunkt muss nach Startzeitpunkt sein.")
        return render_template("FMOF030_create_time_entry.html", person_id=person_id)

    # prüft ob startzeitpunkt in der zukunft liegt
    if (start_zeit.time() > jetzt.time() and datum.date() > jetzt.date()) or datum.date() > jetzt.date():
        flash("Startzeitpunkt muss in der Vergangenheit liegen")
        return render_template("FMOF030_create_time_entry.html", person_id=person_id)

    # prüft ob dieser monat schon gebucht wurde
    datum.strftime("%m.%Y")
    if check_month_booked(datum, klient_id):
        flash("Die Stundennachweise für diesen Monat wurden bereits gebucht, es kann kein Eintrag mehr hinzugefügt "
              "werden")
        return render_template("FMOF030_create_time_entry.html", person_id=person_id)


def base64_to_blob(base64_string):
    # Entfernen des Base64-Header-Teils (wenn vorhanden)
    if "base64," in base64_string:
        base64_string = base64_string.split('base64,')[1]

    # Decodieren des Base64-Strings in Binärdaten
    return base64.b64decode(base64_string)


@create_time_entry_blueprint.route('/create_time_entry/<int:person_id>', methods=['POST', 'GET'])
def submit_arbeitsstunden(person_id):
    if 'user_id' in session:
        user_role = session['user_role']
        if user_role == 'Steuerbüro' or user_role == 'Sachbearbeiter/Kostenträger':
            flash('Sie sind nicht berechtigt diese Seite aufzurufen.')
            return redirect(session['secure_url'])
        else:
            # Rückleitung bei unerlaubter Seite
            session['secure_url'] = url_for('/create_time_entry.submit_arbeitsstunden', person_id=person_id)

            # return url zur rückleitung
            klient_id = session.get('client_id', None)
            return_url = session.get('url')

            # session speichern für rückleitung
            session['url_overlapping'] = url_for('/create_time_entry.submit_arbeitsstunden', person_id=person_id)

            fachkraft = 0

            # klienten für client_dropdown
            klienten = client_dropdown()
            if klient_id is not None:
                client_data = get_klient_data(klient_id)
                if client_data[0][9] == person_id:
                    fachkraft = "1"

            if request.method == 'POST':
                # Eingabedaten aus dem Formular holen
                zeiteintrag_data = {
                    'datum': request.form.get('datum'),
                    'start_zeit': request.form.get('startZeit'),
                    'end_zeit': request.form.get('endZeit'),
                    'fachkraft': "1" if request.form.get('fachkraft') is not None else "0",
                    'klient_id': request.form.get('klientDropdown'),
                    'beschreibung': request.form.get('beschreibung'),
                    'interne_notiz': request.form.get('interneNotiz'),
                    'absage': "1" if request.form.get('absage') is not None else "0"
                }

                ze_signatures = {
                    'neue_unterschrift_klient': request.form.get('signatureDataKlient'),
                    'neue_unterschrift_mitarbeiter': request.form.get('signatureDataMitarbeiter')
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
                        flash(f'Es müssen alle Felder ausgefüllt werden. '
                              f'{field_names[field]} ist noch nicht ausgefüllt.')
                        return render_template('FMOF030_create_time_entry.html', klienten=klienten, person_id=person_id)

                # Konvertiere Datum und Uhrzeit in ein datetime-Objekt
                datum_datetime = datetime.strptime(zeiteintrag_data['datum'], '%Y-%m-%d')
                start_zeit_datetime = datetime.strptime(zeiteintrag_data['start_zeit'], '%H:%M').time()
                end_zeit_datetime = datetime.strptime(zeiteintrag_data['end_zeit'], '%H:%M').time()

                start_datetime = datetime.combine(datum_datetime, start_zeit_datetime)
                end_datetime = datetime.combine(datum_datetime, end_zeit_datetime)
                zeiteintrag_data['start_datetime'] = start_datetime
                zeiteintrag_data['end_datetime'] = end_datetime

                # Prüft ob, Startzeitpunkt vor Endzeitpunkt liegt.
                if not check_time_entry_constraints(datum_datetime, start_datetime, end_datetime,
                                                    zeiteintrag_data['klient_id'], person_id):
                    # Umwandlung der Unterschriften
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

                    # Füge neuen Zeiteintrag hinzu und erhalte die ID
                    zeiteintrag_id = add_zeiteintrag(ze_signatures['neue_unterschrift_mitarbeiter'],
                                                     ze_signatures['neue_unterschrift_klient'],
                                                     start_datetime, end_datetime,
                                                     zeiteintrag_data['klient_id'],
                                                     zeiteintrag_data['fachkraft'],
                                                     zeiteintrag_data['beschreibung'],
                                                     zeiteintrag_data['interne_notiz'],
                                                     zeiteintrag_data['absage'])

                    # Iteriere über alle Fahrt-Einträge und füge sie hinzu
                    fahrt_index = 0
                    fahrt_data_list = []
                    while True:
                        # Werte für jede Fahrt auslesen
                        abrechenbarkeit = 1 if request.form.get(f'abrechenbarkeit{fahrt_index}') else 0
                        start_adresse = request.form.get(f'start_adresse{fahrt_index}')
                        end_adresse = request.form.get(f'end_adresse{fahrt_index}')
                        kilometer = request.form.get(f'kilometer{fahrt_index}')

                        # Überprüfen, ob alle erforderlichen Felder ausgefüllt sind
                        if start_adresse and end_adresse and kilometer:
                            # Konvertieren von Kilometern in einen numerischen Wert und überprüfen auf Null oder negativ
                            try:
                                kilometer = float(kilometer)
                                if kilometer <= 0:
                                    continue  # Überspringt den aktuellen Eintrag, wenn Kilometer ungültig sind
                            except ValueError:
                                continue  # Überspringt den aktuellen Eintrag, wenn Kilometer keine gültige Zahl ist

                            fahrt_data = {
                                'kilometer': kilometer,
                                'start_adresse': start_adresse,
                                'end_adresse': end_adresse,
                                'abrechenbar': abrechenbarkeit,
                                'zeiteintrag_id': zeiteintrag_id
                            }
                            fahrt_data_list.append(fahrt_data)

                            # Datenbankabruf, um die Fahrt hinzuzufügen
                            add_fahrt(kilometer, start_adresse, end_adresse, abrechenbarkeit, zeiteintrag_id)

                        else:
                            # Überprüfen, ob das Ende der Formulardaten erreicht ist
                            if not start_adresse and not end_adresse and not kilometer:
                                break  # Beendet die Schleife, wenn keine weiteren Fahrten vorhanden sind

                        fahrt_index += 1

                    zeiteintrag_data['zeiteintrag_id'] = zeiteintrag_id
                    zeiteintrag_data['mitarbeiter_id'] = person_id

                    print("zeit: ", zeiteintrag_data)

                    session['overlapping_ze'] = zeiteintrag_data
                    print("session: ", session['overlapping_ze'])
                    session['overlapping_fahrten'] = fahrt_data_list
                    session['ze_signatures'] = signatures_path

                    # prüft auf überschneidung einer bestehenden eintragung in der datenbank
                    if check_for_overlapping_zeiteintrag(zeiteintrag_id, start_datetime, end_datetime):
                        return redirect(url_for('check_overlapping_time.overlapping_time',
                                                zeiteintrag_id=zeiteintrag_id))

                    session.pop('client_id')
                    # Weiterleitung zurück zur Herkunftsfunktion
                    flash('Eintrag erfolgreich angelegt')
                    return redirect(return_url)

            return render_template('FMOF030_create_time_entry.html', klient_id=klient_id, klienten=klienten,
                                   return_url=return_url, person_id=person_id, fachkraft=fachkraft)
    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))


def save_blob(blob, path):
    # Überprüfen, ob das Verzeichnis existiert, und wenn nicht, erstellen
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(path, 'wb') as file:
        file.write(blob)
    return path
