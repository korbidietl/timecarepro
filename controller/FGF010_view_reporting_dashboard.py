from datetime import datetime, timedelta
from decimal import Decimal
from flask import Blueprint, render_template, request, flash, session, url_for, redirect
from model.fahrt import sum_km_monatlich
from model.person import sum_hours_mitarbeiter_zeitspanne, sum_absage_mitarbeiter, sum_km_mitarbeiter, \
    mitarbeiter_dropdown
from model.zeiteintrag import get_report_zeiteintrag, get_report_mitarbeiter, sum_mitarbeiter, sum_hours_tabelle, \
    monatliche_gesamtstunden, sum_absage_tabelle, sum_absagen_monatlich, sum_km_monatlich_tabelle
from model.klient import client_dropdown, get_report_klient, sum_hours_klient_zeitspanne, sum_absage_klient, \
    sum_km_klient

reporting_dashboard_blueprint = Blueprint('view_reporting_dashboard', __name__)


@reporting_dashboard_blueprint.route('/reporting_dashboard', methods={'GET', 'POST'})
def reporting_dashboard():
    if 'user_id' in session:
        user_role = session['user_role']
        if user_role != 'Geschäftsführung':
            flash('Sie sind nicht berechtigt diese Seite aufzurufen.')
            return redirect(session['secure_url'])
        else:
            # Rückleitung bei unerlaubter Seite
            session['secure_url'] = url_for('view_reporting_dashboard.reporting_dashboard')

            # Dropdown Felder
            mitarbeiter = mitarbeiter_dropdown()
            ma = {'mitarbeiter': mitarbeiter}

            client = client_dropdown()
            cl = {'klient': client}

            stundendaten = []
            km_diagramm = []
            absagen_diagramm = []

            # Default Werten aktuelles Monat
            date_format = "%Y-%m-%d"
            heute = datetime.now()
            erster_dieses_monats = datetime(heute.year, heute.month, 1)
            von = erster_dieses_monats.strftime(date_format)
            bis = heute.strftime(date_format)

            # Default Werte Jahr
            jahr = datetime.now().year
            start = datetime(jahr, 1, 1)
            end = datetime(jahr, 12, 31)
            start_datum = start.strftime(date_format)
            end_datum = end.strftime(date_format)

            if request.method == 'POST':
                # Filter auslesen
                von_ = request.form.get('von')
                bis_ = request.form.get('bis')
                mitarbeiter = request.form.get('mitarbeiter')
                klient = request.form.get('klient')

                # Überprüfung Eingaben
                valid = True

                try:
                    if von_:
                        datetime.strptime(von_, date_format)
                except ValueError:
                    flash(f"Eingabe in Feld 'von' ungültig.", "error")
                    valid = False

                try:
                    if bis_:
                        datetime.strptime(bis_, date_format)
                except ValueError:
                    flash(f"Eingabe in Feld 'bis' ungültig.", "error")
                    valid = False

                ma_ids = [mitarbeiter_dict['id'] for mitarbeiter_dict in ma['mitarbeiter']]
                if mitarbeiter:
                    try:
                        mitarbeiter_id = int(mitarbeiter)  # Versucht, 'mitarbeiter' in eine Zahl umzuwandeln
                    except ValueError:
                        flash(f"Eingabe in Feld 'Mitarbeiter' ungültig.", "error")
                        valid = False
                    else:
                        if mitarbeiter_id not in ma_ids:
                            flash(f"Eingabe in Feld 'Mitarbeiter' ungültig.", "error")
                            valid = False

                cl_ids = [client_dict['id'] for client_dict in cl['klient']]
                if klient:
                    try:
                        klient_id = int(klient)  # Versucht, 'mitarbeiter' in eine Zahl umzuwandeln
                    except ValueError:
                        flash(f"Eingabe in Feld 'Klient' ungültig.", "error")
                        valid = False
                    else:
                        if klient_id not in cl_ids:
                            flash(f"Eingabe in Feld 'Klient' ungültig.", "error")
                            valid = False

                # Wenn ein Feld ungültig ist erneutes Laden der Seite mit Flash nachricht
                if not valid:
                    return render_template('FGF010_view_reporting_dashboard.html', **ma, **cl,
                                           stundendaten=stundendaten,
                                           terminabsagendaten=absagen_diagramm, kmdaten=km_diagramm)

                # Auswerten des Datums zur weiterverwendung
                if von_:
                    von_date = von_
                    start_datum = von_date
                else:
                    von_date = von

                if bis_:
                    bis_date = bis_
                    end_datum = bis_date
                else:
                    bis_date = bis

                # Umwandlung Filter Werte
                von_formatiert, bis_formatiert = eingabe_formatieren(von_date, bis_date)
                start_datum_formatiert, end_datum_formatiert = eingabe_formatieren(start_datum, end_datum)

                # Überprüfung innerhalb eines Jahres
                if von_formatiert.year != bis_formatiert.year:
                    flash("Die Datumsangaben müssen innerhalb des gleichen Jahres liegen.", "error")
                    valid = False

                # Ausgabe Tabellen
                kl_tabelle_gesamt = klienten_tabelle(von_formatiert, bis_formatiert, klient, mitarbeiter)
                klienten_liste = get_report_klient(von_formatiert, bis_formatiert, klient, mitarbeiter)
                ma_tabelle_gesamt = mitarbeiter_tabelle(von_formatiert, bis_formatiert, klient, mitarbeiter)
                mitarbeiter_liste = get_report_mitarbeiter(von_formatiert, bis_formatiert, klient, mitarbeiter)
                zeiteintraege_liste = get_report_zeiteintrag(von_formatiert, bis_formatiert, klient, mitarbeiter)
                ze_tabelle_gesamt = zeiteintraege_tabelle(von_formatiert, bis_formatiert, klient, mitarbeiter)

                # Ausgabe Diagramme
                maanzahl = mitarbeiter_anzahl()
                stunden_diagramm = monatliche_gesamtstunden(start_datum_formatiert, end_datum_formatiert, mitarbeiter,
                                                            klient)
                stundendaten = [float(d) if isinstance(d, Decimal) else d for d in stunden_diagramm]
                absagen_diagramm = sum_absagen_monatlich(start_datum_formatiert, end_datum_formatiert, mitarbeiter,
                                                         klient)
                km_diagramm = sum_km_monatlich(start_datum_formatiert, end_datum_formatiert, mitarbeiter, klient)

                return render_template('FGF010_view_reporting_dashboard.html', **ma, **cl,
                                       klienten_daten=klienten_liste,
                                       mitarbeiter_daten=mitarbeiter_liste, zeiteintraege_liste=zeiteintraege_liste,
                                       klient_gesamt=kl_tabelle_gesamt, mitarbeiter_gesamt=ma_tabelle_gesamt,
                                       stundendaten=stundendaten, ze_gesamt=ze_tabelle_gesamt,
                                       terminabsagendaten=absagen_diagramm, kmdaten=km_diagramm, mazahl=maanzahl)

            # Umwandlung Default Werte
            von_formatiert, bis_formatiert = eingabe_formatieren(von, bis)
            start_datum_formatiert, end_datum_formatiert = eingabe_formatieren(start_datum, end_datum
                                                                               )
            # Ausgaben Tabellen
            kl_tabelle_gesamt = klienten_tabelle(von_formatiert, bis_formatiert, None, None)
            klienten_liste = get_report_klient(von_formatiert, bis_formatiert)
            ma_tabelle_gesamt = mitarbeiter_tabelle(von_formatiert, bis_formatiert, None, None)
            mitarbeiter_liste = get_report_mitarbeiter(von_formatiert, bis_formatiert)
            zeiteintraege_liste = get_report_zeiteintrag(von_formatiert, bis_formatiert)
            ze_tabelle = zeiteintraege_tabelle(von_formatiert, bis_formatiert, None, None)

            # Ausgabe Diagramme
            maanzahl = mitarbeiter_anzahl()
            stunden_diagramm = monatliche_gesamtstunden(start_datum_formatiert, end_datum_formatiert)
            stundendaten = [float(d) if isinstance(d, Decimal) else d for d in stunden_diagramm]
            absagen_diagramm = sum_absagen_monatlich(start_datum_formatiert, end_datum_formatiert)
            km_diagramm = sum_km_monatlich(start_datum_formatiert, end_datum_formatiert)

            return render_template('FGF010_view_reporting_dashboard.html', **ma, **cl, klienten_daten=klienten_liste,
                                   mitarbeiter_daten=mitarbeiter_liste, zeiteintraege_liste=zeiteintraege_liste,
                                   klient_gesamt=kl_tabelle_gesamt, mitarbeiter_gesamt=ma_tabelle_gesamt,
                                   stundendaten=stundendaten, ze_gesamt=ze_tabelle,
                                   terminabsagendaten=absagen_diagramm, kmdaten=km_diagramm, mazahl=maanzahl)
    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))


def eingabe_formatieren(von, bis):
    von_date = datetime.strptime(von, '%Y-%m-%d').date()
    bis_date = datetime.strptime(bis, '%Y-%m-%d').date()
    von = datetime.combine(von_date, datetime.min.time())
    bis = datetime.combine(bis_date, datetime.max.time())
    return von, bis


def stunden_addieren(data):
    total_hours = 0
    total_minutes = 0

    for _, _, _, _, duration in data:
        hours, minutes = duration.split(':')

        total_hours += int(hours)
        total_minutes += int(minutes)

    # Minuten in Stunden umrechnen und zur Gesamtstundenanzahl hinzufügen
    total_hours += total_minutes // 60
    total_minutes = total_minutes % 60

    return f"{total_hours:02d}:{total_minutes:02d}"


def absagen_addieren(data):
    total_absagen = 0

    for _, _, _, _, absagen in data:
        total_absagen += absagen

    return total_absagen


def km_addieren(data):
    total_kilometer = 0
    abrechenbare_kilometer = 0
    nicht_abrechenbare_kilometer = 0

    for _, _, _, _, gesamt_km, abrechenbar_km, nicht_abrechenbar_km in data:
        total_kilometer += gesamt_km
        abrechenbare_kilometer += abrechenbar_km
        nicht_abrechenbare_kilometer += nicht_abrechenbar_km

    return total_kilometer, abrechenbare_kilometer, nicht_abrechenbare_kilometer


def klienten_tabelle(von, bis, client_id, user_id):
    if client_id:
        client_id_int = int(client_id)
    elif user_id:
        user_id_int = int(user_id)
    # Gesamt Stunden

    klstunden = sum_hours_klient_zeitspanne(von, bis)
    if client_id:
        filtered_data_s = [record for record in klstunden if record[0] == client_id_int]
        klient_stunden = stunden_addieren(filtered_data_s)
    elif user_id:
        filtered_data_s = [record for record in klstunden if record[1] == user_id_int]
        klient_stunden = stunden_addieren(filtered_data_s)
    else:
        klient_stunden = stunden_addieren(klstunden)

    # Gesamt Absagen
    klabsage = sum_absage_klient(von, bis)
    if client_id:
        filtered_data_a = [record for record in klabsage if record[0] == client_id_int]
        klient_absagen = absagen_addieren(filtered_data_a)
    elif user_id:
        filtered_data_a = [record for record in klabsage if record[1] == user_id_int]
        klient_absagen = absagen_addieren(filtered_data_a)
    else:
        klient_absagen = absagen_addieren(klabsage)

    # Gesamt KM
    klkm = sum_km_klient(von, bis)
    if client_id:
        filtered_data_k = [record for record in klkm if record[0] == client_id_int]
        klient_km_total, klient_km_abrechenbar, klient_km_nicht_abrechenbar = km_addieren(filtered_data_k)
    elif user_id:
        filtered_data_k = [record for record in klkm if record[1] == user_id_int]
        klient_km_total, klient_km_abrechenbar, klient_km_nicht_abrechenbar = km_addieren(filtered_data_k)
    else:
        klient_km_total, klient_km_abrechenbar, klient_km_nicht_abrechenbar = km_addieren(klkm)

    return klient_km_total, klient_km_abrechenbar, klient_km_nicht_abrechenbar, klient_absagen, klient_stunden


def mitarbeiter_tabelle(von, bis, client_id, user_id):
    if user_id:
        user_id_int = int(user_id)
    elif client_id:
        client_id_int = int(client_id)
    # Gesamt Stunden
    mastunden = sum_hours_mitarbeiter_zeitspanne(von, bis)
    if user_id:
        filtered_data_s = [record for record in mastunden if record[0] == user_id_int]
        mitarbeiter_stunden = stunden_addieren(filtered_data_s)
    elif client_id:
        filtered_data_s = [record for record in mastunden if record[1] == client_id_int]
        mitarbeiter_stunden = stunden_addieren(filtered_data_s)
    else:
        mitarbeiter_stunden = stunden_addieren(mastunden)

    # Gesamt Absagen
    maabsage = sum_absage_mitarbeiter(von, bis)
    if user_id:
        filtered_data_a = [record for record in maabsage if record[0] == user_id_int]
        mitarbeiter_absagen = absagen_addieren(filtered_data_a)
    elif client_id:
        filtered_data_a = [record for record in maabsage if record[1] == client_id_int]
        mitarbeiter_absagen = absagen_addieren(filtered_data_a)
    else:
        mitarbeiter_absagen = absagen_addieren(maabsage)

    # Gesamt KM
    makm = sum_km_mitarbeiter(von, bis)
    if user_id:
        filtered_data_k = [record for record in makm if record[0] == user_id_int]
        mitarbeiter_km_total, mitarbeiter_km_abrechenbar, mitarbeiter_km_nicht_abrechenbar = km_addieren(
            filtered_data_k)
    elif client_id:
        filtered_data_k = [record for record in makm if record[1] == client_id_int]
        mitarbeiter_km_total, mitarbeiter_km_abrechenbar, mitarbeiter_km_nicht_abrechenbar = km_addieren(
            filtered_data_k)
    else:
        mitarbeiter_km_total, mitarbeiter_km_abrechenbar, mitarbeiter_km_nicht_abrechenbar = km_addieren(makm)

    return (mitarbeiter_km_total, mitarbeiter_km_abrechenbar, mitarbeiter_km_nicht_abrechenbar, mitarbeiter_absagen,
            mitarbeiter_stunden)


def zeiteintraege_tabelle(von, bis, client_id, user_id):
    stunden = sum_hours_tabelle(von, bis, client_id, user_id)
    absagen = sum_absage_tabelle(von, bis, client_id, user_id)
    km = sum_km_monatlich_tabelle(von, bis, client_id, user_id)
    km_ges = km['gesamt_km']
    km_abr = km['abrechenbare_km']
    km_n_abr = km['nicht_abrechenbare_km']
    return stunden, absagen, km_ges, km_abr, km_n_abr


def mitarbeiter_anzahl():
    # aktuellen Monat und Jahr
    jetzt = datetime.now()
    aktueller_monat = jetzt.month
    aktuelles_jahr = jetzt.year

    mazahl = sum_mitarbeiter(aktueller_monat, aktuelles_jahr)
    return mazahl
