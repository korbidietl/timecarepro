import datetime
import io
import csv

from flask import Blueprint, render_template, request, session, Response
from datetime import datetime
from db_query import get_client_name, get_sachbearbeiter_name, get_fallverantwortung_id, check_booked

client_hours_blueprint = Blueprint('client_hours_blueprint', __name__, template_folder='templates')


def generate_month_year_combinations():
    aktuelles_jahr = datetime.now().year
    monate = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
              'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
    kombinationen = []

    for jahr in range(aktuelles_jahr - 5, aktuelles_jahr + 1):
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


@client_hours_blueprint.route('/client_supervision_hours/<int:client_id>', methods=['POST', 'GET'])
def client_supervision_hours(client_id):
    kombinationen = generate_month_year_combinations()

    # auswahl des angezeigten Zeitraums
    if request.method == 'POST':
        gewaehlte_kombination = request.form.get('monat_jahr')
    else:
        # Standardmäßig aktuelles Monat und Jahr
        monate = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                  'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
        aktuelles_jahr = datetime.now().year
        aktueller_monat = datetime.now().month
        gewaehlte_kombination = f"{monate[aktueller_monat - 1]} {aktuelles_jahr}"

    monat, jahr = extrahiere_jahr_und_monat(gewaehlte_kombination)

    # Abrufe aus der Datenbank
    client_name = get_client_name(client_id)
    # client_name = f"{client_data[0]} {client_data[1]}"
    client_sachbearbeiter_name = get_sachbearbeiter_name(client_id)
    #client_sachbearbeiter_name = f"{client_sachbearbeiter_data[0]} {client_sachbearbeiter_data[1]}"
    fallverantwortung_id = get_fallverantwortung_id(client_id)
    fallverantwortung = False

    # Rolle und ID aus der Session
    user_id = session.get('user_id')
    user_role = session.get('user_role')

    # Überprüfen ob Fallverantwortung hat
    if user_id == fallverantwortung_id:
        fallverantwortung = True
        # Datenbankaufruf für alle anzeigen
        #zeiteintraege_liste = get_zeiteintraege_for_client(client_id, monat, jahr)
        #booked = check_booked(zeiteintraege_liste.zeiteintrags_id)
        #return render_template('FMOF010_show_supervisionhours_client.html', zeiteintraege_liste=zeiteintraege_liste)

    elif user_id != fallverantwortung_id:
        fallverantwortung = False
        # Zeiteinträge nur von eigener ID (ohne Fallverantwortung)
       # zeiteintraege_liste_of = get_zeiteintraege_for_client_of(client_id)
        #booked = check_booked(zeiteintraege_liste_of.zeiteintrags_id)
        #return render_template('FMOF010_show_supervisionhours_client.html', zeiteintraege_liste=zeiteintraege_liste_of)

    return render_template('/FMOF010_show_supervisionhours_client.html', client_id=client_id, client_name=client_name,
                           client_sachbearbeiter=client_sachbearbeiter_name, fallverantwortung=fallverantwortung,
                           user_id=user_id, user_role=user_role, gewaehlte_kombination=gewaehlte_kombination,
                           kombinationen=kombinationen)


# Für Export
def generiere_csv_daten(zeiteintraege_liste):
    output = io.StringIO()
    writer = csv.writer(output)

    # Beispiel: Schreiben der Kopfzeilen
    writer.writerow(['Datum', 'Beschreibung', 'Kilometer', 'Anfang', 'Ende', 'Mitarbeitet', 'Unterschrift KLient',
                     'Unterschrift Mitarbeiter'])

    # Schreiben der Datenzeilen
    for zeiteintrag in zeiteintraege_liste:
        writer.writerow([zeiteintrag.datum, zeiteintrag.stunden, zeiteintrag.beschreibung, zeiteintrag.kilometer,
                         zeiteintrag.anfang, zeiteintrag.ende, zeiteintrag.mitarbieter, zeiteintrag.unterschrift_klient,
                         zeiteintrag.unterschrift_mitarbeiter])

    return output.getvalue()


@client_hours_blueprint.route('/exportieren/<int:client_id>', methods=['POST'])
def exportieren_client(client_id):
   # zeiteintraege_liste = get_zeiteintraege_for_client(client_id)
   # csv_daten = generiere_csv_daten(zeiteintraege_liste)

    return Response(
     #   csv_daten,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=uebersicht.csv"}
    )
