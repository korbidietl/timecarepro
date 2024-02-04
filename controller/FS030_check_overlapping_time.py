from flask import Blueprint, request, render_template, session, url_for, redirect, flash
from controller.FMOF050_edit_time_entry import save_after_overlapping
from model.klient import get_client_name
from model.person import get_name_by_id
from model.zeiteintrag import check_for_overlapping_zeiteintrag, get_zeiteintrag_by_id

check_overlapping_time_blueprint = Blueprint('check_overlapping_time', __name__)


@check_overlapping_time_blueprint.route('/check_overlapping_time/<int:zeiteintrag_id>', methods=['GET', 'POST'])
def overlapping_time(zeiteintrag_id):
    if 'user_id' in session:
        session['secure_url'] = url_for('check_overlapping_time.overlapping_time', zeiteintrag_id=zeiteintrag_id)
        return_url = session.get('url_overlapping')
        zeiteintrag_data = session.get('overlapping_ze')
        fahrten_data_list = session.get('overlapping_fahrten')
        ze_signatures = session.get('ze_signatures')

        if request.method == 'POST':
            session['ueberschneidung'] = 0
            save_after_overlapping(zeiteintrag_id, zeiteintrag_data, fahrten_data_list, ze_signatures)
            return redirect(return_url)

        print("ze in overlapping: ", zeiteintrag_data)
        overlapping_entries = []
        if zeiteintrag_data:
            # Füge den formatierten originalen Zeiteintrag hinzu
            overlapping_entries.append(format_zeiteintrag(zeiteintrag_data))
            print("in schleife")

            start_zeit_datetime = zeiteintrag_data['start_datetime']
            end_zeit_datetime = zeiteintrag_data['end_datetime']

            overlapping_ids = check_for_overlapping_zeiteintrag(zeiteintrag_id, start_zeit_datetime, end_zeit_datetime)
            for entry_id in overlapping_ids:
                entry_data = get_zeiteintrag_by_id(entry_id)[0]
                overlapping_entries.append(format_zeiteintrag_new(entry_data))

        return render_template('FS030_check_overlapping_time.html',
                               overlapping_entries=overlapping_entries,
                               original_zeiteintrag_id=zeiteintrag_id,
                               return_url=return_url, fahrten_data_list=fahrten_data_list)
    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))


def format_zeiteintrag(entry):
    datum = entry['datum']
    startzeit = entry['start_zeit']
    endzeit = entry['end_zeit']
    mitarbeiter = get_name_by_id(entry['mitarbeiter_id'])
    m_vorname = mitarbeiter[0][0]
    m_nachname = mitarbeiter[0][1]
    client = get_client_name(entry['klient_id'])
    c_vorname = client[0]
    c_nachname = client[1]
    zeiteintrag_id = entry['zeiteintrag_id']
    beschreibung = entry['beschreibung']
    return zeiteintrag_id, datum, startzeit, endzeit, beschreibung, m_nachname, m_vorname, c_nachname, c_vorname


def format_zeiteintrag_new(entry):
    datum = entry[3].strftime('%Y-%m-%d')
    startzeit = entry[3].strftime('%H:%M')
    endzeit = entry[4].strftime('%H:%M')
    mitarbeiter = get_name_by_id(entry[5])
    m_vorname = mitarbeiter[0][0]
    m_nachname = mitarbeiter[0][1]
    client = get_client_name(entry[6])
    c_vorname = client[0]
    c_nachname = client[1]
    return entry[0], datum, startzeit, endzeit, entry[8], m_nachname, m_vorname, c_nachname, c_vorname
