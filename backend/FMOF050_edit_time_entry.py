from flask import Blueprint, request, redirect, url_for, render_template
from db_query import get_zeiteintrag_with_fahrten_by_id, edit_zeiteintrag, delete_fahrt, add_fahrt, edit_fahrt
from datetime import datetime

edit_time_entry_blueprint = Blueprint('edit_time_entry', __name__)


@edit_time_entry_blueprint.route('/edit_time_entry/<int:zeiteintrag_id>', methods=['GET', 'POST'])
def edit_time_entry(zeiteintrag_id):
    if request.method == 'GET':
        # Daten für den zu bearbeitenden Zeiteintrag holen
        zeiteintrag_data = get_zeiteintrag_with_fahrten_by_id(zeiteintrag_id)
        return render_template("edit_time_entry.html", zeiteintrag=zeiteintrag_data['zeiteintrag'],
                               fahrten=zeiteintrag_data['fahrten'], zeiteintrag_id=zeiteintrag_id)
    else:
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
        start_datetime = datetime.strptime(f"{datum} {start_zeit}", '%Y-%m-%d %H:%M')
        end_datetime = datetime.strptime(f"{datum} {end_zeit}", '%Y-%m-%d %H:%M')

        # Änderungen am Zeiteintrag speichern
        edit_zeiteintrag(zeiteintrag_id, start_zeit, end_zeit, unterschrift_klient, unterschrift_mitarbeiter, klient_id, beschreibung, interne_notiz, absage)

        # Bearbeite Fahrt-Einträge
        existing_fahrten_ids = request.form.getlist('existing_fahrten_ids')
        for fahrt_id in existing_fahrten_ids:
            if request.form.get(f'kilometer{fahrt_id}') is None:
                # Falls kein Kilometer-Feld vorhanden ist, lösche die Fahrt
                delete_fahrt(fahrt_id)
            else:
                # Ansonsten aktualisiere die Fahrt
                edit_fahrt(fahrt_id, kilometer=request.form[f'kilometer{fahrt_id}'],
                           abrechenbar=request.form.get(f'abrechenbarkeit{fahrt_id}', False),
                           start_adresse=request.form[f'start_adresse{fahrt_id}'],
                           end_adresse=request.form[f'end_adresse{fahrt_id}'],
                           zeiteintrag_id=zeiteintrag_id)

        # Füge neue Fahrten hinzu
        for i in range(fahrtCounter):  # fahrtCounter sollte vom Frontend übergeben werden
            if f'kilometer_new{i}' in request.form:
                add_fahrt(kilometer=request.form[f'kilometer_new{i}'],
                        start_adresse=request.form[f'start_adresse_new{i}'],
                        end_adresse=request.form[f'end_adresse_new{i}'],
                        abrechenbar=request.form.get(f'abrechenbarkeit_new{i}', False),
                        zeiteintrag_id=zeiteintrag_id)


        # Weiterleitung zurück zur Übersicht der abgelegten Stunden
        return redirect(url_for('show_supervisionhours_client'))
