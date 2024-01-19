from flask import Blueprint, request, render_template, session, url_for, redirect

from FMOF050_edit_time_entry import save_after_overlapping
from db_query import (check_for_overlapping_zeiteintrag, get_zeiteintrag_by_id, get_name_by_id, get_client_name)

check_overlapping_time_blueprint = Blueprint('check_overlapping_time', __name__)


@check_overlapping_time_blueprint.route('/check_overlapping_time/<int:zeiteintrag_id>', methods=['GET', 'POST'])
def overlapping_time(zeiteintrag_id):
    session['secure_url'] = url_for('check_overlapping_time.overlapping_time', zeiteintrag_id=zeiteintrag_id)
    return_url = session.get('url_overlapping')
    zeiteintrag_data = get_zeiteintrag_by_id(zeiteintrag_id)
    fahrten_data_list = session.get('overlapping_fahrten')

    if request.method == 'POST':
        save_after_overlapping(zeiteintrag_id, zeiteintrag_data, fahrten_data_list)
        return redirect(return_url)

    overlapping_entries = []
    if zeiteintrag_data:
        # Füge den formatierten originalen Zeiteintrag hinzu
        orig_entry = zeiteintrag_data[0]
        overlapping_entries.append(format_zeiteintrag(orig_entry))

        start_zeit_datetime = orig_entry[3]
        end_zeit_datetime = orig_entry[4]

        overlapping_ids = check_for_overlapping_zeiteintrag(zeiteintrag_id, start_zeit_datetime, end_zeit_datetime)
        for entry_id in overlapping_ids:
            entry_data = get_zeiteintrag_by_id(entry_id)[0]
            overlapping_entries.append(format_zeiteintrag(entry_data))

    return render_template('FS030_check_overlapping_time.html',
                           overlapping_entries=overlapping_entries,
                           original_zeiteintrag_id=zeiteintrag_id,
                           return_url=return_url, fahrten_data_list=fahrten_data_list)


def format_zeiteintrag(entry):
    datum = entry[3].strftime('%Y-%m-%d')
    startzeit = entry[3].strftime('%H:%M')
    endzeit = entry[4].strftime('%H:%M')
    mitarbeiter = get_name_by_id(entry[5])
    m_vorname = mitarbeiter[0][0]
    m_nachname = mitarbeiter[0][1]
    print("mit: ", m_nachname, m_vorname)
    client = get_client_name(entry[6])
    c_vorname = client[0]
    c_nachname = client[1]
    print("klie: ", c_nachname, c_vorname)
    return entry[0], datum, startzeit, endzeit, entry[8], m_nachname, m_vorname, c_nachname, c_vorname
