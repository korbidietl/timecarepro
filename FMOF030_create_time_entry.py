import base64

from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from db_query import add_zeiteintrag, add_fahrt, check_for_overlapping_zeiteintrag, check_month_booked, client_dropdown
from datetime import datetime

create_time_entry_blueprint = Blueprint('/create_time_entry', __name__)

# test
def check_time_entry_constraints(datum, start_zeit, end_zeit, klient_id):
    # Prüft ob, Startzeitpunkt vor Endzeitpunkt liegt.
    jetzt = datetime.now()
    if start_zeit >= end_zeit:
        flash("Endzeitpunkt muss nach Startzeitpunkt sein.")
        return render_template("FMOF030_create_time_entry.html")

    # prüft ob startzeitpunkt in der zukunft liegt
    if (start_zeit.time() > jetzt.time() and datum.date() > jetzt.date()) or datum.date() > jetzt.date():
        flash("Startzeitpunkt muss in der Vergangenheit liegen")
        return render_template("FMOF030_create_time_entry.html")

    # prüft ob dieser monat schon gebucht wurde
    datum.strftime("%m.%Y")
    if check_month_booked(datum, klient_id):
        flash("Die Stundennachweise für diesen Monat wurden bereits gebucht, es kann kein Eintrag mehr hinzugefügt "
              "werden")
        return render_template("FMOF030_create_time_entry.html")


def base64_to_blob(base64_string):
    # Entfernen des Base64-Header-Teils (wenn vorhanden)
    if "base64," in base64_string:
        base64_string = base64_string.split('base64,')[1]

    # Decodieren des Base64-Strings in Binärdaten
    return base64.b64decode(base64_string)


@create_time_entry_blueprint.route('/create_time_entry', methods=['POST', 'GET'])
def submit_arbeitsstunden():
    # return url zur rückleitung
    if session['client_id']:
        klient_id = session.get('client_id')
    else:
        klient_id = ""

    print(klient_id)
    return_url = session.get('url')
    # session speichern für rückleitung
    session['url_overlapping'] = url_for('/create_time_entry.submit_arbeitsstunden')

    # klienten für client_dropdown
    klienten = client_dropdown()

    if request.method == 'POST':
        # Eingabedaten aus dem Formular holen
        datum = request.form.get('datum')
        start_zeit = request.form.get('startZeit')
        end_zeit = request.form.get('endZeit')
        fachkraft = "1" if request.form.get('fachkraft') is not None else "0"
        klient_id = request.form.get('klientDropdown')
        beschreibung = request.form.get('beschreibung')
        interne_notiz = request.form.get('interneNotiz')
        unterschrift_klient = request.form.get('signatureDataKlient')
        unterschrift_mitarbeiter = request.form.get('signatureDataMitarbeiter')
        absage = "1" if request.form.get('absage') is not None else "0"

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
                return render_template('FMOF030_create_time_entry.html', klienten=klienten)

        # Konvertiere Datum und Uhrzeit in ein datetime-Objekt
        datum_datetime = datetime.strptime(datum, '%Y-%m-%d')
        start_zeit_datetime = datetime.strptime(start_zeit, '%H:%M').time()
        end_zeit_datetime = datetime.strptime(end_zeit, '%H:%M').time()

        start_datetime = datetime.combine(datum_datetime, start_zeit_datetime)
        end_datetime = datetime.combine(datum_datetime, end_zeit_datetime)

        # Prüft ob, Startzeitpunkt vor Endzeitpunkt liegt.
        if not check_time_entry_constraints(datum_datetime, start_datetime, end_datetime, klient_id):

            # Umwandlung der Unterschriften
            if unterschrift_klient:
                unterschrift_klient = base64_to_blob(unterschrift_klient)

            if unterschrift_mitarbeiter:
                unterschrift_mitarbeiter = base64_to_blob(unterschrift_mitarbeiter)


            # Füge neuen Zeiteintrag hinzu und erhalte die ID
            zeiteintrag_id = add_zeiteintrag(unterschrift_mitarbeiter, unterschrift_klient, start_datetime,
                                             end_datetime, klient_id, fachkraft, beschreibung, interne_notiz,
                                             absage)

            # Iteriere über alle Fahrt-Einträge und füge sie hinzu
            fahrt_index = 0
            while True:
                # Werte für jede Fahrt auslesen
                abrechenbarkeit = request.form.get(f'abrechenbarkeit{fahrt_index}') == 'on'
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

                    # Datenbankabruf, um die Fahrt hinzuzufügen
                    add_fahrt(kilometer, start_adresse, end_adresse, abrechenbarkeit, zeiteintrag_id)

                else:
                    # Überprüfen, ob das Ende der Formulardaten erreicht ist
                    if not start_adresse and not end_adresse and not kilometer:
                        break  # Beendet die Schleife, wenn keine weiteren Fahrten vorhanden sind

                fahrt_index += 1

            # prüft auf überschneidung einer bestehenden eintragung in der datenbank
            if check_for_overlapping_zeiteintrag(zeiteintrag_id, klient_id, start_datetime, end_datetime):
                return redirect(url_for('check_overlapping_time.overlapping_time', zeiteintrag_id=zeiteintrag_id))
        session.pop('client_id')
        # Weiterleitung zurück zur Herkunftsfunktion
        flash('Eintrag erfolgreich angelegt')
        return redirect(return_url)

    return render_template('FMOF030_create_time_entry.html', klient_id=klient_id, klienten=klienten, return_url=return_url)
