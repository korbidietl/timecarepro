from flask import Blueprint, render_template, request, session
from db_query import get_client_table_client_sb, check_for_overlapping_zeiteintrag, check_booked, get_client_name, \
    get_sachbearbeiter_name
from FMOF010_show_supervisionhours_client import generate_month_year_combinations, extrahiere_jahr_und_monat, \
    convert_blob_to_base64, check_ueberschneidung_liste, check_booked_liste
from datetime import datetime

access_hours_km_clients_blueprint = Blueprint("access_hours_km_clients", __name__)


def unterschriften_liste(zeiteintrag_ids):
    u_liste = []
    for zeiteintrag in zeiteintrag_ids:
        # Blob der Unterschriften
        u_k = zeiteintrag[8]
        u_m = zeiteintrag[9]
        # Umwandlung Blob
        u_k_base64 = convert_blob_to_base64(u_k)
        u_m_base64 = convert_blob_to_base64(u_m)
        # Hinzufügen zu Liste
        u_liste.append((u_k_base64, u_m_base64))
    return u_liste


@access_hours_km_clients_blueprint.route('/access_hours_km_clients/<int:client_id>', methods=['GET', 'POST'])
def view_time_entries(client_id):
    user_id = session.get('user_id')

    kombinationen = generate_month_year_combinations()
    aktuelles_jahr = datetime.now().year
    aktueller_monat = datetime.now().month

    # Auswahl des angezeigten Zeitraums
    if request.method == 'POST':
        gewaehlte_kombination = request.form.get('monat_jahr')
    else:
        # Standardmäßig aktuelles Monat und Jahr
        monate = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                  'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']

        gewaehlte_kombination = f"{monate[aktueller_monat - 1]} {aktuelles_jahr}"

    month, year = extrahiere_jahr_und_monat(gewaehlte_kombination)

    client_name = get_client_name(client_id)
    zeiteintrag_ids = get_client_table_client_sb(client_id, user_id, month, year)
    u_liste = unterschriften_liste(zeiteintrag_ids)
    ueberschneidung_liste = check_ueberschneidung_liste(zeiteintrag_ids, client_id)
    booked_liste = check_booked_liste(zeiteintrag_ids)
    kombinierte_liste = list(zip(zeiteintrag_ids, ueberschneidung_liste, booked_liste, u_liste))

    return render_template('FSK010_access_hours_km_clients.html',
                           client_id=client_id, kombinierte_liste=kombinierte_liste, client_name=client_name,
                           gewaehlte_kombination=gewaehlte_kombination, kombinationen=kombinationen)
