from flask import Blueprint, render_template, request, session
from db_query import get_client_table, get_client_table_sb
from FMOF010_show_supervisionhours_client import generate_month_year_combinations, extrahiere_jahr_und_monat
from datetime import datetime

show_clients_blueprint = Blueprint("show_clients", __name__)


@show_clients_blueprint.route('/show_clients', methods=['GET', 'POST'])
def show_clients():
    person = session.get('user_id')
    role = session.get('user_role')

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

    if role == "Sachbearbeiter/Kostenträger":
        clients = get_client_table_sb(person, month, year)
    else:
        clients = get_client_table(month, year)
    if not clients:
        return render_template('FAN040_show_client_table.html', person=person, clients=[], gewaehlte_kombination= gewaehlte_kombination, kombinationen=kombinationen, role=role,
                                       no_clients_message="Keine Klienten vorhanden.")

    return render_template('FAN040_show_client_table.html', person=person, clients=clients, gewaehlte_kombination= gewaehlte_kombination, kombinationen=kombinationen, role=role)

