from flask import Blueprint, request, render_template, session, url_for, redirect

from FMOF050_edit_time_entry import save_after_overlapping
from db_query import (check_for_overlapping_zeiteintrag, get_zeiteintrag_by_id, get_name_by_id, get_client_name)

check_overlapping_time_blueprint = Blueprint('check_overlapping_time', __name__)


@check_overlapping_time_blueprint.route('/check_overlapping_time/<int:zeiteintrag_id>', methods=['GET', 'POST'])
def overlapping_time(zeiteintrag_id):
    # Rückleitung bei unerlaubter Seite
    session['secure_url'] = url_for('check_overlapping_time.overlapping_time', zeiteintrag_id=zeiteintrag_id)

    return_url = session.get('url_overlapping')
    zeiteintrag_data = session.get('overlapping_ze')
    fahrten_data_list = session.get('overlapping_fahrten')

    overlapping_entries = []

    # auf Button speichern geklickt
    if request.method == 'POST':
        save_after_overlapping(zeiteintrag_id, zeiteintrag_data, fahrten_data_list)
        # Redirect oder render_template hier, je nachdem, was nach dem Speichern passieren soll
        return redirect(return_url)
    # Standartverhalten beim Aufruf der Funktion
    overlapping_entries_details = []
    if zeiteintrag_data:
        # Extrahieren der benötigten Daten aus dem ersten Ergebnis
        start_zeit_datetime = zeiteintrag_data['start_datetime']
        end_zeit_datetime = zeiteintrag_data['end_datetime']
        klient_id = zeiteintrag_data['klient_id']
        mitarbeiter_id = zeiteintrag_data['mitarbeiter_id']

        overlapping_ids = check_for_overlapping_zeiteintrag(zeiteintrag_id, start_zeit_datetime,
                                                            end_zeit_datetime)
        matching_entries = []
        for entry_id in overlapping_ids:
            entry_data_list = get_zeiteintrag_by_id(entry_id)
            if entry_data_list:
                entry_data = entry_data_list[0]

                if mitarbeiter_id == entry_data[5] or klient_id == entry_data[6]:
                    matching_entries.append(entry_data[0])

        for entry in matching_entries:
            if entry:
                z_id = entry[0]
                startzeit_obj = entry[3]
                endzeit_obj = entry[4]

                # Extrahieren der Uhrzeit als String
                startzeit = startzeit_obj.strftime('%H:%M')
                endzeit = endzeit_obj.strftime('%H:%M')
                datum = startzeit_obj.strftime('%Y-%m-%d')

                beschreibung = entry[8]
                mitarbeiter_id = entry[5]
                mitarbeiter_list = get_name_by_id(mitarbeiter_id)
                mitarbeiter = mitarbeiter_list[0]
                m_vorname = mitarbeiter[0]
                m_nachname = mitarbeiter[1]
                client_id = entry[6]
                client = get_client_name(client_id)
                c_vorname = client[0]
                c_nachname = client[1]

                overlapping_entries.append(
                    (z_id, datum, startzeit, endzeit, beschreibung, m_vorname, m_nachname, c_vorname, c_nachname))

    return render_template('FS030_check_overlapping_time.html',
                           overlapping_entries=overlapping_entries, original_zeiteintrag_id=zeiteintrag_id,
                           return_url=return_url)
