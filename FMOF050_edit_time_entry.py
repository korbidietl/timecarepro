import base64

from flask import Blueprint, request, redirect, url_for, render_template, session
from db_query import (edit_zeiteintrag, delete_fahrt, add_fahrt, edit_fahrt,
                      fahrt_id_existing, check_for_overlapping_zeiteintrag, get_zeiteintrag_by_id,
                      get_fahrt_by_zeiteintrag, get_klient_data, client_dropdown)
from datetime import datetime
from FMOF030_create_time_entry import check_time_entry_constraints, base64_to_blob

edit_time_entry_blueprint = Blueprint('edit_time_entry', __name__)


@edit_time_entry_blueprint.route('/edit_time_entry/<int:zeiteintrag_id>', methods=['GET', 'POST'])
def edit_time_entry(zeiteintrag_id):

    # session speichern für rückleitung
    session['url'] = url_for('edit_time_entry.edit_time_entry', zeiteintrag_id=zeiteintrag_id)

    # klienten für client_dropdown
    klienten = client_dropdown()

    zeiteintrag_liste = get_zeiteintrag_by_id(zeiteintrag_id)
    zeiteintrag = zeiteintrag_liste[0]
    datum = zeiteintrag[3].strftime("%Y-%m-%d")
    von = zeiteintrag[3].strftime("%H:%M")
    bis = zeiteintrag[4].strftime("%H:%M")

    fahrten = get_fahrt_by_zeiteintrag(zeiteintrag_id)

    # Name Klient
    klient_id = zeiteintrag[6]
    klient_data = get_klient_data(klient_id)
    klient_name = klient_data[0][1] + ' ' + klient_data[0][2]

    # Umwandlung Unterschriften
    if zeiteintrag[1]:
        unterschrift_mitarbeiter = base64.b64encode(zeiteintrag[1]).decode('utf-8')
    else:
        unterschrift_mitarbeiter = ""

    if zeiteintrag[2]:
        unterschrift_klient = base64.b64encode(zeiteintrag[2]).decode('utf-8')
    else:
        unterschrift_klient = ""

    if request.method == 'POST':
        # Eingabedaten aus dem Formular holen
        datum = request.form.get('datum')
        start_zeit = request.form.get('startZeit')
        end_zeit = request.form.get('endZeit')
        klient_id = request.form.get('klient')
        beschreibung = request.form.get('beschreibung')
        interne_notiz = request.form.get('interneNotiz')
        neue_unterschrift_klient = request.form.get('signatureDataKlient')
        neue_unterschrift_mitarbeiter = request.form.get('signatureDataMitarbeiter')
        absage = request.form.get('absage')

        # Konvertiere Datum und Uhrzeit in ein datetime-Objekt
        datum_datetime = datetime.strptime(f"{datum}", '%Y-%m-%d')
        start_datetime = datetime.strptime(f"{start_zeit}", '%H:%M')
        end_datetime = datetime.strptime(f"{end_zeit}", '%H:%M')

        if not check_time_entry_constraints(datum_datetime, start_datetime, end_datetime, klient_id):
            # Umwandlung der Unterschriften
            if neue_unterschrift_klient:
                neue_unterschrift_klient = base64_to_blob(neue_unterschrift_klient)
            if neue_unterschrift_mitarbeiter:
                neue_unterschrift_mitarbeiter = base64_to_blob(neue_unterschrift_mitarbeiter)

            # Änderungen am Zeiteintrag speichern
            edit_zeiteintrag(zeiteintrag_id, datum_datetime, start_datetime, end_datetime, neue_unterschrift_klient,
                             neue_unterschrift_mitarbeiter, klient_id, beschreibung, interne_notiz, absage)
            if check_for_overlapping_zeiteintrag(zeiteintrag_id, klient_id, start_datetime, end_datetime):
                return redirect(url_for('/check_overlapping_time', zeiteintrag_id=zeiteintrag_id))
        else:
            check_time_entry_constraints(datum_datetime, start_datetime, end_datetime, klient_id)

        # importiere fahrtCounter von html hidden input in python
        fahrtCounter = int(request.form.get('fahrtCounterInput', 1))

        # Bearbeite Fahrt-Einträge
        existing_fahrten_ids = request.form.getlist('existing_fahrten_ids')
        for fahrt_id in existing_fahrten_ids:
            # aktualisiere die Fahrt
            edit_fahrt(fahrt_id=request.form[f'fahrt_id{fahrt_id}'], kilometer=request.form[f'kilometer{fahrt_id}'],
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
        return redirect(url_for('show_supervisionhours_client.show_supervisionhours_client'))

    return render_template("FMOF050_edit_time_entry.html", zeiteintrag=zeiteintrag, fahrten=fahrten,
                           klient_name=klient_name, datum=datum, von=von, bis=bis,
                           unterschrift_klient=unterschrift_klient,
                           unterschrift_mitarbeiter=unterschrift_mitarbeiter, zeiteintrag_id=zeiteintrag_id, klienten=klienten)
