from flask import Blueprint, render_template, request, redirect, url_for, session
from db_query import get_zeiteintrag_for_person, get_zeiteintrag_with_fahrten_by_id, check_booked
from FMOF010_show_supervisionhours_client import generate_month_year_combinations, extrahiere_jahr_und_monat
from datetime import datetime

view_time_entries_blueprint = Blueprint("view_time_entries", __name__)


@view_time_entries_blueprint.route('/view_time_entries/<int:person_id>', methods=['GET', 'POST'])
def view_time_entries(person_id):
    person = session.get('user_id')
    session['url'] = url_for('view_time_entries.view_time_entries', person_id=person_id)

    # Dropdown Feld Zeitauswahl
    kombinationen = generate_month_year_combinations()
    aktuelles_jahr = datetime.now().year
    aktueller_monat = datetime.now().month

    # auswahl des angezeigten Zeitraums
    if request.method == 'POST':
        gewaehlte_kombination = request.form.get('monat_jahr')
    else:
        # Standardmäßig aktuelles Monat und Jahr
        monate = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                  'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']

        gewaehlte_kombination = f"{monate[aktueller_monat - 1]} {aktuelles_jahr}"

    month, year = extrahiere_jahr_und_monat(gewaehlte_kombination)

    if request.method == 'POST':

        zeiteintrag_ids = get_zeiteintrag_for_person(person_id, month, year)

        time_entries = []

        for zeiteintrag_id in zeiteintrag_ids:
            zeiteintrag_with_fahrten = get_zeiteintrag_with_fahrten_by_id(zeiteintrag_id)
            for entry in zeiteintrag_with_fahrten:
                entry['zeiteintrag']['kilometer'] = sum([fahrt['kilometer'] for fahrt in entry['fahrten']])
                entry['zeiteintrag']['buchung_vorhanden'] = check_booked(entry['zeiteintrag']['id'])
                time_entries.append(entry['zeiteintrag'])

        return render_template('FMOF020_view_time_entries.html', person=person, time_entries=time_entries, kombinationen=kombinationen, gewaehlte_kombination=gewaehlte_kombination)
    else:
        return render_template('FMOF020_view_time_entries.html', person=person, time_entries=[], kombinationen=kombinationen, gewaehlte_kombination=gewaehlte_kombination)
