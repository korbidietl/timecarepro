from flask import Blueprint, render_template, request, redirect, url_for, session
from db_query import get_person_by_id, get_time_entries_by_person_id, get_fahrten_by_zeiteintrag_id, check_booked

view_time_entries_blueprint = Blueprint("view_time_entries", __name__, template_folder='templates')

@view_time_entries_blueprint.route('/view_time_entries/<int:person_id>', methods=['GET', 'POST'])
def view_time_entries(person_id):
    person = get_person_by_id(person_id)
    if request.method == 'POST':
        month = request.form['month']
        time_entries = get_time_entries_by_person_id(person_id, month)
        for entry in time_entries:
            entry['kilometer'] = sum([fahrt['kilometer'] for fahrt in get_fahrten_by_zeiteintrag_id(entry['id'])])
            entry['buchung_vorhanden'] = check_booked(entry['id'])
        return render_template('view_time_entries.html', person=person, time_entries=time_entries)
    else:
        return render_template('view_time_entries.html', person=person, time_entries=[])
