from flask import Blueprint, request, redirect, url_for, render_template, flash
from db_query import add_zeiteintrag, add_fahrt, check_for_overlapping_zeiteintrag
from datetime import datetime
from FS020_sign_capture import capture_signature

create_time_entry_blueprint = Blueprint('create_time_entry', __name__)


@create_time_entry_blueprint.route('/create_time_entry', methods=['POST', 'GET'])
def submit_arbeitsstunden():
    # Eingabedaten aus dem Formular holen
    datum = request.form.get('datum')
    start_zeit = request.form.get('startZeit')
    end_zeit = request.form.get('endZeit')
    # da müssen wir uns noch überlegen, wie das am besten sinn macht
    # weil klient name kann ja doppelt sein, aber das dropdown soll ja keine id anzeigen
    # wie erkennt man aber im dropdown welcher max mustermann der richtige ist?
    klient_id = request.form.get('klient')
    beschreibung = request.form.get('beschreibung')
    interne_notiz = request.form.get('interneNotiz')
    # hier müssen noch unterschriften rein
    unterschrift_klient = capture_signature()
    unterschrift_mitarbeiter = capture_signature()
    absage = request.form.get('absage')

    # Konvertiere Datum und Uhrzeit in ein datetime-Objekt
    datum_datetime = datetime.strptime(f"{datum}", '%Y-%m-%d')
    start_datetime = datetime.strptime(f"{start_zeit}", '%H:%M')
    end_datetime = datetime.strptime(f"{end_zeit}", '%H:%M')

    # Prüft ob, Startzeitpunkt vor Endzeitpunkt liegt.
    if start_datetime >= end_datetime:
        flash("Endzeitpunkt muss nach Startzeitpunkt sein.")
        return render_template("FMOF030_create_time_entry.html")

    # Füge neuen Zeiteintrag hinzu und erhalte die ID
    else:
        zeiteintrag_id = add_zeiteintrag(datum_datetime, start_datetime, end_datetime, beschreibung, interne_notiz,
                                         unterschrift_klient, unterschrift_mitarbeiter, absage)

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
        if check_for_overlapping_zeiteintrag(zeiteintrag_id, klient_id, start_zeit, end_zeit):
            # überschneidungs funktion einfügen
            return

    # Weiterleitung zurück zur Übersicht der abgelegten Stunden
    return redirect(url_for('show_supervisionhours_client'))



