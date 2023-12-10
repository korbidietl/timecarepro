import datetime

from flask import Blueprint, render_template, request, session
from datetime import datetime
client_hours_blueprint = Blueprint('client_hours_blueprint', __name__, template_folder='templates')

def generate_month_year_combinations():
    aktuelles_jahr = datetime.now().year
    monate = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
              'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
    kombinationen = []

    for jahr in range(aktuelles_jahr-5, aktuelles_jahr+1):
        for monat_index, monat in enumerate(monate, start=1):
            kombinationen.append(f"{monat} {jahr}")

    return kombinationen

@client_hours_blueprint.route('/client/<int:client_id>')
def client_profile(client_id):
    client_id = request.form.get('client_id')
    # Abrufe aus der Datenbank
    client_name = get_client_name(client_id)
    client_sachbearbeiter = get_sachbearbeiter_name(client_id)
    fallverantwortung_id =

    # Rolle aus der Session
    user_id = session.get('user_id')
    user_role = session.get('user_role')




    # Überprüfen ob Fallverantwortung hat
    if user_id == fallverantwortung_id:

    else:



    return render_template('show_supervisionhours_client.html', client_id=client_id, client_name = client_name,client_sachbearbeiter= client_sachbearbeiter)

@client_hours_blueprint.route('/ihre_route', methods=['GET', 'POST'])
def ihre_view_funktion():
    kombinationen = generate_month_year_combinations()
    gewaehlte_kombination = request.form.get('monat_jahr') if request.method == 'POST' else kombinationen[-1]
    # Verarbeiten Sie die Auswahl
    return render_template('ihre_template.html', kombinationen=kombinationen, gewaehlte_kombination=gewaehlte_kombination)
