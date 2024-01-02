from flask import Blueprint, render_template, request, redirect, url_for, session
from db_query import get_zeiteintrag_for_client, get_zeiteintrag_with_fahrten_by_id, check_booked

view_time_entries_blueprint = Blueprint("view_time_entries", __name__)


@view_time_entries_blueprint.route('/view_time_entries/<int:person_id>', methods=['GET', 'POST'])
def view_time_entries(person_id):
    person = session.get('user_id')

    session['url'] = url_for('view_time_entries.view_time_entries', person_id=person_id)
    if request.method == 'POST':
        monat = request.form['month']
        jahr = request.form['year']

        # funktionsnamen get_zeiteintrag... noch ändern --> ist nicht aktuell
        zeiteintrag_ids = get_zeiteintrag_for_client(monat, jahr)

        time_entries = []

        for zeiteintrag_id in zeiteintrag_ids:
            zeiteintrag_with_fahrten = get_zeiteintrag_with_fahrten_by_id(zeiteintrag_id)
            for entry in zeiteintrag_with_fahrten:
                entry['zeiteintrag']['kilometer'] = sum([fahrt['kilometer'] for fahrt in entry['fahrten']])
                entry['zeiteintrag']['buchung_vorhanden'] = check_booked(entry['zeiteintrag']['id'])
                time_entries.append(entry['zeiteintrag'])

        return render_template('FMOF020_view_time_entries.html', person=person, time_entries=time_entries)
    else:
        return render_template('FMOF020_view_time_entries.html', person=person, time_entries=[])
