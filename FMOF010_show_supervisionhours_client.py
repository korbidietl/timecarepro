import base64
import datetime
from flask import Blueprint, render_template, request, session, url_for, flash, redirect
from datetime import datetime
from db_query import get_client_name, get_sachbearbeiter_name, get_fallverantwortung_id, \
    get_zeiteintrag_for_client_and_person, check_for_overlapping_zeiteintrag, check_booked, \
    get_zeiteintrag_for_client, sum_hours_klient, sum_km_klient_ges

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


def check_booked_liste(zeiteintraege_liste):
    # Liste ob Eintrag gebuch
    booked_liste = []
    for zeiteintrag in zeiteintraege_liste:
        booked_status = check_booked(zeiteintrag[0])
        booked_liste.append(booked_status)
    return booked_liste


def check_ueberschneidung_liste(zeiteintraege_liste):
    # Liste für Überschneidungen
    ueberschneidung_liste = []
    for zeiteintrag in zeiteintraege_liste:
        z_id = zeiteintrag[0]
        datum_str = zeiteintrag[1]
        von_str = zeiteintrag[4]
        bis_str = zeiteintrag[5]

        datum = datetime.strptime(datum_str, '%d.%m.%Y').date()
        von = datetime.strptime(von_str, "%H:%M").time()
        bis = datetime.strptime(bis_str, "%H:%M").time()

        von_datum = datetime.combine(datum, von)
        bis_datum = datetime.combine(datum, bis)

        ueberschneidung = check_for_overlapping_zeiteintrag(z_id, von_datum, bis_datum)
        # Überprüfen, ob die Liste leer ist
        if ueberschneidung:
            ueberschneidungs_status = "Ja"
        else:
            ueberschneidungs_status = "Nein"

        ueberschneidung_liste.append(ueberschneidungs_status)

    return ueberschneidung_liste


def convert_blob_to_base64(blob):
    if blob is not None:
        return base64.b64encode(blob).decode()
    return None


def unterschriften_liste(zeiteintraege_liste):
    u_liste = []
    for zeiteintrag in zeiteintraege_liste:
        # Blob der Unterschriften
        u_k = zeiteintrag[9]
        u_m = zeiteintrag[10]
        # Umwandlung Blob
        u_k_base64 = convert_blob_to_base64(u_k)
        u_m_base64 = convert_blob_to_base64(u_m)
        # Hinzufügen zu Liste
        u_liste.append((u_k_base64, u_m_base64))
    return u_liste


@client_hours_blueprint.route('/client_supervision_hours/<int:client_id>', methods=['POST', 'GET'])
def client_supervision_hours(client_id):
    if 'user_id' in session:
        # Rückleitung bei unerlaubter Seite
        session['secure_url'] = url_for('client_hours_blueprint.client_supervision_hours', client_id=client_id)

        # Für Rückleitung
        session['url'] = url_for('client_hours_blueprint.client_supervision_hours', client_id=client_id)
        session['client_id'] = client_id

        # Rolle und ID aus der Session
        user_id = session.get('user_id')
        user_role = session.get('user_role')

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

        # Abrufe aus der Datenbank
        client_name = get_client_name(client_id)
        client_sachbearbeiter_name = get_sachbearbeiter_name(client_id)
        fallverantwortung_id = get_fallverantwortung_id(client_id)
        fallverantwortung = user_id == fallverantwortung_id

        # Überprüfen ob Fallverantwortung hat
        if fallverantwortung or user_role in ['Verwaltung', 'Geschäftsführung']:
            # Gesamt Stunden auslesen
            sum_hours_list = sum_hours_klient(client_id, month, year)
            sum_hours = []
            if sum_hours_list:
                sum_hours = sum_hours_list[0]

            # Gesamt Kilometer auslesen
            sum_km_list = sum_km_klient_ges(client_id, month, year)
            sum_km = []
            if sum_km_list:
                sum_km = sum_km_list[0]

            # Listen erstellen
            zeiteintraege_liste = get_zeiteintrag_for_client(client_id, month, year)
            u_liste = unterschriften_liste(zeiteintraege_liste)
            ueberschneidung_liste = check_ueberschneidung_liste(zeiteintraege_liste)
            booked_liste = check_booked_liste(zeiteintraege_liste)

            # Listen kombinieren
            kombinierte_liste = list(zip(zeiteintraege_liste, ueberschneidung_liste, booked_liste, u_liste))

            return render_template('FMOF010_show_supervisionhours_client.html', user_id=user_id,
                                   client_id=client_id,
                                   kombinierte_liste=kombinierte_liste,
                                   client_name=client_name,
                                   client_sachbearbeiter=client_sachbearbeiter_name,
                                   user_role=user_role, gewaehlte_kombination=gewaehlte_kombination,
                                   kombinationen=kombinationen, sum_km=sum_km, sum_hours=sum_hours,
                                   fallverantwortung=fallverantwortung)

        else:
            # Gesamt Stunden auslesen
            sum_hours_list = sum_hours_klient(client_id, month, year, user_id)
            sum_hours = []
            if sum_hours_list:
                sum_hours = sum_hours_list[0]

            # Gesamt Kilometer auslesen
            sum_km_list = sum_km_klient_ges(client_id, month, year, user_id)
            sum_km = []
            if sum_km_list:
                sum_km = sum_km_list[0]
            # Listen erstellen
            zeiteintraege_liste = get_zeiteintrag_for_client_and_person(client_id, user_id, month, year)
            u_liste = unterschriften_liste(zeiteintraege_liste)
            ueberschneidung_liste = check_ueberschneidung_liste(zeiteintraege_liste)
            booked_liste = check_booked_liste(zeiteintraege_liste)

            # Listen kombinieren
            kombinierte_liste = list(zip(zeiteintraege_liste, ueberschneidung_liste, booked_liste, u_liste))

            return render_template('FMOF010_show_supervisionhours_client.html', user_id=user_id,
                                   client_id=client_id,
                                   kombinierte_liste=kombinierte_liste,
                                   client_name=client_name,
                                   client_sachbearbeiter=client_sachbearbeiter_name,
                                   fallverantwortung=fallverantwortung,
                                   user_role=user_role, gewaehlte_kombination=gewaehlte_kombination,
                                   kombinationen=kombinationen, sum_km=sum_km, sum_hours=sum_hours)

    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))
