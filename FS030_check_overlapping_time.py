from datetime import datetime

from flask import Blueprint, request, redirect, url_for, render_template
from db_query import check_for_overlapping_zeiteintrag, get_zeiteintrag_by_id, get_zeiteintrag_with_fahrten_by_id, get_name_by_id

check_overlapping_time_blueprint = Blueprint('check_overlapping_time', __name__)


@check_overlapping_time_blueprint.route('/check_overlapping_time/<int:zeiteintrag_id>', methods=['GET', 'POST'])
def overlapping_time(zeiteintrag_id):

    zeiteintrag_data = get_zeiteintrag_by_id(zeiteintrag_id)

    if zeiteintrag_data:
        # Extrahieren der benötigten Daten aus dem ersten Ergebnis
        einzelner_zeiteintrag = zeiteintrag_data[0]
        klient_id = einzelner_zeiteintrag[6]
        startzeit = einzelner_zeiteintrag[3]
        endzeit = einzelner_zeiteintrag[4]

    overlapping_ids = check_for_overlapping_zeiteintrag(zeiteintrag_id, klient_id, startzeit, endzeit)
    overlapping_entries = []

    for ids in overlapping_ids:
        entry_data = get_zeiteintrag_by_id(ids)
        if entry_data:

            z_id = entry_data[0]
            startzeit_str = entry_data[3]
            endzeit_str = entry_data[4]
            startzeit_obj = datetime.strptime(startzeit_str, '%Y-%m-%d %H:%M:%S')
            endzeit_obj = datetime.strptime(endzeit_str, '%Y-%m-%d %H:%M:%S')

            # Extrahieren der Uhrzeit als String
            startzeit = startzeit_obj.strftime('%H:%M')
            endzeit = endzeit_obj.strftime('%H:%M')
            datum = startzeit_obj.strftime('%Y-%m-%d')

            beschreibung = entry_data[8]
            mitarbeiter_id = entry_data[5]
            mitarbeiter = get_name_by_id(mitarbeiter_id)
            client_id = entry_data[6]
            client = get_name_by_id(client_id)

            overlapping_entries.append((z_id, datum, startzeit,endzeit,beschreibung,mitarbeiter, client))

    return render_template('FS030_check_overlapping_time.html', overlapping_entries=overlapping_entries,
                           original_zeiteintrag_id=zeiteintrag_id)
