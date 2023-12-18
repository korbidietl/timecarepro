from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for
from FMOF050_edit_time_entry import edit_time_entry
from db_query import get_zeiteintrag_with_fahrten_by_id, edit_zeiteintrag, delete_fahrt, edit_fahrt, add_fahrt
edit_time_entry_fv_blueprint = Blueprint('edit_time_entry_fv', __name__)


@edit_time_entry_fv_blueprint.route('/edit_time_entry_fv/<int:zeiteintrag_id>', methods=['GET', 'POST'])
def edit_time_entry(zeiteintrag_id):
    if request.method == 'GET':
        # Daten für den zu bearbeitenden Zeiteintrag holen
        zeiteintrag_data = get_zeiteintrag_with_fahrten_by_id(zeiteintrag_id)
        return render_template("FV100_edit_time_entry_fv.html", zeiteintrag=zeiteintrag_data['zeiteintrag'],
                               fahrten=zeiteintrag_data['fahrten'], zeiteintrag_id=zeiteintrag_id)
    else:
        # Eingabedaten aus dem Formular holen
        datum = request.form.get('datum')
        start_zeit = request.form.get('startZeit')
        end_zeit = request.form.get('endZeit')
        klient_id = request.form.get('klient')
        beschreibung = request.form.get('beschreibung')
        interne_notiz = request.form.get('interneNotiz')
        # Unterschriften sollten nicht übernommen werden, da dies keine sicheren Methoden sind
        #absage = request.form.get('absage')

        # Konvertiere Datum und Uhrzeit in ein datetime-Objekt
        start_datetime = datetime.strptime(f"{datum} {start_zeit}", '%Y-%m-%d %H:%M')
        end_datetime = datetime.strptime(f"{datum} {end_zeit}", '%Y-%m-%d %H:%M')

        # Änderungen am Zeiteintrag speichern
        edit_zeiteintrag(zeiteintrag_id, start_datetime, end_datetime, klient_id, beschreibung, interne_notiz)

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
        for i in range(fahrtCounter): # fahrtCounter sollte vom Frontend übergeben werden
            if f'kilometer_new{i}' in request.form:
                add_fahrt(kilometer=request.form[f'kilometer_new{i}'],
                        start_adresse=request.form[f'start_adresse_new{i}'],
                        end_adresse=request.form[f'end_adresse_new{i}'],
                        abrechenbar=request.form.get(f'abrechenbarkeit_new{i}', False),
                        zeiteintrag_id=zeiteintrag_id)

        # Weiterleitung zurück zur Übersicht der abgelegten Stunden
        return redirect(url_for('show_supervisionhours_client'))