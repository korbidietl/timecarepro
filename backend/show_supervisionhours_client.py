import datetime

from flask import Blueprint, render_template, request, session
from datetime import datetime
from db_query import get_client_name, get_sachbearbeiter_name, get_fallverantwortung_id, check_booked
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

def extrahiere_jahr_und_monat(kombination):
    teile = kombination.split(' ')
    monat_name = teile[0]
    jahr = teile[1]

    # Umwandlung des Monatsnamens in eine Nummer (Januar = 1, Februar = 2, usw.)
    monate = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
              'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
    monat_nummer = monate.index(monat_name) + 1

    return monat_nummer, int(jahr)

@client_hours_blueprint.route('/client/<int:client_id>', methods='POST')
def client_profile(client_id):
    kombinationen = generate_month_year_combinations()

    if request.method =='POST':
        gewaehlte_kombination = request.form.get('monat_jahr')
    else:
        #Standardmäßig aktuelles Monat und Jahr
        monate = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                  'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
        aktuelles_jahr = datetime.now().year
        aktueller_monat = datetime.now().month
        gewaehlte_kombination = f"{monate[aktueller_monat - 1]} {aktuelles_jahr}"

    monat, jahr = extrahiere_jahr_und_monat(gewaehlte_kombination)

    # Abrufe aus der Datenbank
    client_name = get_client_name(client_id)
    client_sachbearbeiter = get_sachbearbeiter_name(client_id)
    fallverantwortung_id = get_fallverantwortung_id(client_id)

    # Rolle aus der Session
    user_id = session.get('user_id')
    user_role = session.get('user_role')



    # Überprüfen ob Fallverantwortung hat
    if user_id == fallverantwortung_id:
        # Datenbankaufruf für alle anzeigen
        zeiteintraege_liste = get_zeiteintraege_for_client(client_id, monat, jahr)
        return render_template('show_supervisionhours_client.html', zeiteintraege_liste=zeiteintraege_liste

    else:
        # Datenbankaufrug für Mitarbeiter_ID anzeigen



    return render_template('show_supervisionhours_client.html', client_id=client_id, client_name = client_name,client_sachbearbeiter= client_sachbearbeiter)

@client_hours_blueprint.route('/monat_auswahl', methods=['GET', 'POST'])
def monat_auswahl():

    gewaehlte_kombination = request.form.get('monat_jahr') if request.method == 'POST' else kombinationen[-1]
    # Verarbeiten Sie die Auswahl
    return render_template('show_supervisionhours_client.html', kombinationen=kombinationen, gewaehlte_kombination=gewaehlte_kombination)
