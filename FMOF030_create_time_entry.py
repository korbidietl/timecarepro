import base64
import time

from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from db_query import add_zeiteintrag, add_fahrt, check_for_overlapping_zeiteintrag, check_month_booked
from datetime import datetime
from FS020_sign_capture import capture_signature

create_time_entry_blueprint = Blueprint('/create_time_entry', __name__)


def check_time_entry_constraints(datum, startZeit, endZeit, klientID):
    # Prüft ob, Startzeitpunkt vor Endzeitpunkt liegt.
    if startZeit >= endZeit:
        flash("Endzeitpunkt muss nach Startzeitpunkt sein.")
        return render_template("FMOF030_create_time_entry.html")

    # prüft ob startzeitpunkt in der zukunft liegt
    if startZeit > time.strftime("%H:%M") or datum > time.strftime("%d.%m.%Y"):
        flash("Der Startzeitpunkt darf nicht in der Zukunft liegen!")
        return render_template("FMOF030_create_time_entry.html")

    # prüft ob dieser monat schon gebucht wurde
    datum.strftime("%m.%Y")
    if check_month_booked(datum, klientID):
        flash("Dieser Monat wurde von den ausgewählten Klienten bereits gebucht!")
        return render_template("FMOF030_create_time_entry.html")


def base64_to_blob(base64_string):
    # Entfernen des Base64-Header-Teils (wenn vorhanden)
    if "base64," in base64_string:
        base64_string = base64_string.split('base64,')[1]

    # Decodieren des Base64-Strings in Binärdaten
    return base64.b64decode(base64_string)


@create_time_entry_blueprint.route('/create_time_entry', methods=['POST', 'GET'])
def submit_arbeitsstunden():
    session['url'] = url_for('/create_time_entry.submit_arbeitsstunden')

    if request.method == 'POST':
        # Eingabedaten aus dem Formular holen
        datum = request.form.get('datum')
        start_zeit = request.form.get('startZeit')
        end_zeit = request.form.get('endZeit')
        fachkraft = request.form.get('fachkraft')
        klient_id = request.form.get('klient')
        beschreibung = request.form.get('beschreibung')
        interne_notiz = request.form.get('interneNotiz')
        unterschrift_klient = request.form.get('signatureDataKlient')
        unterschrift_mitarbeiter = capture_signature('signatureDataKlient')
        absage = request.form.get('absage')

        # Konvertiere Datum und Uhrzeit in ein datetime-Objekt
        datum_datetime = datetime.strptime(f"{datum}", '%Y-%m-%d')
        start_datetime = datetime.strptime(f"{start_zeit}", '%H:%M')
        end_datetime = datetime.strptime(f"{end_zeit}", '%H:%M')

        # Prüft ob, Startzeitpunkt vor Endzeitpunkt liegt.
        if not check_time_entry_constraints(datum_datetime, start_datetime, end_datetime, klient_id):
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
                abrechenbarkeit = request.form.get(f'abrechenbarkeit{fahrt_index}')
                start_adresse = request.form.get(f'start_adresse{fahrt_index}')
                end_adresse = request.form.get(f'end_adresse{fahrt_index}')
                kilometer = request.form.get(f'kilometer{fahrt_index}')
                if kilometer is None:
                    break  # Keine weiteren Fahrten im Formular
                add_fahrt(zeiteintrag_id, abrechenbarkeit, start_adresse, end_adresse, kilometer)
                fahrt_index += 1

            # prüft auf überschneidung einer bestehenden eintragung in der datenbank
            if check_for_overlapping_zeiteintrag(zeiteintrag_id, klient_id, start_datetime, end_datetime):
                return redirect(url_for('/check_overlapping_time', zeiteintrag_id=zeiteintrag_id))

        # Weiterleitung zurück zur Übersicht der abgelegten Stunden
        return redirect(url_for('client_supervision_hours', client_id=klient_id))

    return render_template('FMOF030_create_time_entry.html')
