from flask import Blueprint, render_template, request, url_for, session, flash, redirect
from model.zeiteintrag import get_zeiteintrag_for_person
from model.person import get_role_by_id, get_name_by_id
from controller.FMOF010_show_supervisionhours_client import generate_month_year_combinations, extrahiere_jahr_und_monat, \
    convert_blob_to_base64, check_booked_liste
from datetime import datetime

view_time_entries_blueprint = Blueprint("view_time_entries", __name__)


def unterschriften_liste(zeiteintrag):
    u_liste = []
    for eintrag in zeiteintrag:
        # Blob der Unterschriften
        u_k = eintrag[7]
        u_m = eintrag[8]
        # Umwandlung Blob
        u_k_base64 = convert_blob_to_base64(u_k)
        u_m_base64 = convert_blob_to_base64(u_m)
        # Hinzufügen zu Liste
        u_liste.append((u_k_base64, u_m_base64))
    return u_liste


@view_time_entries_blueprint.route('/view_time_entries/<int:person_id>', methods=['GET', 'POST'])
def view_time_entries(person_id):
    if 'user_id' in session:
        user_role = session['user_role']
        if user_role == 'Steuerbüro' or user_role == 'Sachbearbeiter/Kostenträger':
            flash('Sie sind nicht berechtigt diese Seite aufzurufen.')
            return redirect(session['secure_url'])
        else:
            # Rückleitung bei unerlaubter Seite
            session['secure_url'] = url_for('view_time_entries.view_time_entries', person_id=person_id)

            # session daten speichern
            session.pop('client_id', None)
            session['url'] = url_for('view_time_entries.view_time_entries', person_id=person_id)

            # Name und Role für Überschrift
            name_list = get_name_by_id(person_id)
            name = name_list[0]
            role = get_role_by_id(person_id)

            # Dropdown Feld Zeitauswahl
            kombinationen = generate_month_year_combinations()
            aktuelles_jahr = datetime.now().year
            aktueller_monat = datetime.now().month
            monate = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                      'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']

            # Auswahl des angezeigten Zeitraums
            if request.method == 'POST':
                gewaehlte_kombination = request.form.get('monat_jahr')
            else:
                # Standardmäßig aktuelles Monat und Jahr
                gewaehlte_kombination = f"{monate[aktueller_monat - 1]} {aktuelles_jahr}"

            month, year = extrahiere_jahr_und_monat(gewaehlte_kombination)

            # Abfragen der Zeiteinträge
            zeiteintrag = get_zeiteintrag_for_person(person_id, month, year)
            u_liste = unterschriften_liste(zeiteintrag)
            booked_liste = check_booked_liste(zeiteintrag)

            if zeiteintrag and u_liste and booked_liste:
                kombinierte_liste = zip(zeiteintrag, u_liste, booked_liste)
            else:
                kombinierte_liste = []

            return render_template('FMOF020_view_time_entries.html', person_id=person_id, name=name, role=role,
                                   kombinationen=kombinationen, gewaehlte_kombination=gewaehlte_kombination,
                                   kombinierte_liste=kombinierte_liste)

    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))
