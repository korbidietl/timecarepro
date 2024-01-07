from flask import Blueprint, request, render_template, session
from db_query import (check_for_overlapping_zeiteintrag, get_zeiteintrag_by_id, get_name_by_id, get_client_name,
                      delete_zeiteintrag)

check_overlapping_time_blueprint = Blueprint('check_overlapping_time', __name__)


@check_overlapping_time_blueprint.route('/check_overlapping_time/<int:zeiteintrag_id>', methods=['GET', 'POST'])
def overlapping_time(zeiteintrag_id):
    return_url = session.get('url_overlapping')
    overlapping_entries = []

    zeiteintrag_data = get_zeiteintrag_by_id(zeiteintrag_id)

    if zeiteintrag_data:
        # Extrahieren der benötigten Daten aus dem ersten Ergebnis
        einzelner_zeiteintrag = zeiteintrag_data[0]
        klient_id = einzelner_zeiteintrag[6]
        startzeit = einzelner_zeiteintrag[3]
        endzeit = einzelner_zeiteintrag[4]

        overlapping_ids = check_for_overlapping_zeiteintrag(zeiteintrag_id, klient_id, startzeit, endzeit)
        overlapping_ids.append(zeiteintrag_id)

        for ids in overlapping_ids:
            entry_data_list = get_zeiteintrag_by_id(ids)
            entry_data = entry_data_list[0]
            if entry_data:
                z_id = entry_data[0]
                startzeit_obj = entry_data[3]
                endzeit_obj = entry_data[4]

                # Extrahieren der Uhrzeit als String
                startzeit = startzeit_obj.strftime('%H:%M')
                endzeit = endzeit_obj.strftime('%H:%M')
                datum = startzeit_obj.strftime('%Y-%m-%d')

                beschreibung = entry_data[8]
                mitarbeiter_id = entry_data[5]
                mitarbeiter_list = get_name_by_id(mitarbeiter_id)
                mitarbeiter = mitarbeiter_list[0]
                m_vorname = mitarbeiter[0]
                m_nachname = mitarbeiter[1]
                client_id = entry_data[6]
                client = get_client_name(client_id)
                c_vorname = client[0]
                c_nachname = client[1]

                overlapping_entries.append(
                    (z_id, datum, startzeit, endzeit, beschreibung, m_vorname, m_nachname, c_vorname, c_nachname))

    if request.method == 'POST':
        delete_zeiteintrag(zeiteintrag_id)

    return render_template('FS030_check_overlapping_time.html', overlapping_entries=overlapping_entries,
                           original_zeiteintrag_id=zeiteintrag_id, return_url=return_url)
