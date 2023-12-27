from flask import Blueprint, request, redirect, url_for, render_template
from db_query import (get_zeiteintrag_with_fahrten_by_id, edit_zeiteintrag, delete_fahrt, add_fahrt, edit_fahrt,
                      fahrt_id_existing, check_for_overlapping_zeiteintrag)
from datetime import datetime
from FMOF030_create_time_entry import check_time_entry_constraints
from FS020_sign_capture import capture_signature


edit_time_entry_blueprint = Blueprint('edit_time_entry', __name__)


@edit_time_entry_blueprint.route('/edit_time_entry/<int:zeiteintrag_id>', methods=['GET', 'POST'])
def edit_time_entry(zeiteintrag_id):
    if request.method == 'GET':
        # Daten für den zu bearbeitenden Zeiteintrag holen
        zeiteintrag_data = get_zeiteintrag_with_fahrten_by_id(zeiteintrag_id)
        return render_template("FMOF050_edit_time_entry.html", zeiteintrag=zeiteintrag_data['zeiteintrag'],
                               fahrten=zeiteintrag_data['fahrten'], zeiteintrag_id=zeiteintrag_id)
    else:
        # Eingabedaten aus dem Formular holen
        datum = request.form.get('datum')
        start_zeit = request.form.get('startZeit')
        end_zeit = request.form.get('endZeit')
        klient_id = request.form.get('klient')
        beschreibung = request.form.get('beschreibung')
        interne_notiz = request.form.get('interneNotiz')
        unterschrift_klient = capture_signature()
        unterschrift_mitarbeiter = capture_signature()
        absage = request.form.get('absage')

        # Konvertiere Datum und Uhrzeit in ein datetime-Objekt
        datum_datetime = datetime.strptime(f"{datum}", '%Y-%m-%d')
        start_datetime = datetime.strptime(f"{start_zeit}", '%H:%M')
        end_datetime = datetime.strptime(f"{end_zeit}", '%H:%M')

        if not check_time_entry_constraints(datum_datetime, start_datetime, end_datetime, klient_id):
            # Änderungen am Zeiteintrag speichern
            edit_zeiteintrag(zeiteintrag_id, datum_datetime, start_datetime, end_datetime, unterschrift_klient, unterschrift_mitarbeiter, klient_id, beschreibung, interne_notiz, absage)
            check_for_overlapping_zeiteintrag(zeiteintrag_id, klient_id, start_datetime, end_datetime)
        else:
            check_time_entry_constraints(datum_datetime, start_datetime, end_datetime, klient_id)

        # importiere fahrtCounter von html hidden input in python
        fahrtCounter = int(request.form.get('fahrtCounterInput', 1))

        # Bearbeite Fahrt-Einträge
        existing_fahrten_ids = request.form.getlist('existing_fahrten_ids')
        for fahrt_id in existing_fahrten_ids:
            # aktualisiere die Fahrt
            edit_fahrt(fahrt_id = request.form[f'fahrt_id{fahrt_id}'], kilometer=request.form[f'kilometer{fahrt_id}'],
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
        return redirect(url_for('show_supervisionhours_client'))
