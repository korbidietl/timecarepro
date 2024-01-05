from datetime import datetime
from decimal import Decimal

from flask import Blueprint, render_template, url_for, request, flash, redirect
from db_query import mitarbeiter_dropdown, client_dropdown, sum_mitarbeiter, sum_hours_mitarbeiter_zeitspanne, \
    sum_hours_klient_zeitspanne, \
    sum_absage_mitarbeiter, sum_absage_klient, sum_km_mitarbeiter, sum_km_klient, get_report_zeiteintrag, \
    get_report_mitarbeiter, get_report_klient, monatliche_gesamtstunden, sum_absagen_monatlich, sum_km_monatlich

reporting_dachboard_blueprint = Blueprint('view_reporting_dashboard', __name__)


@reporting_dachboard_blueprint.route('/reporting_dashboard', methods={'GET', 'POST'})
def reporting_dashboard():
    # Dropdown Felder
    mitarbeiter = mitarbeiter_dropdown()
    ma = {'mitarbeiter': mitarbeiter}

    client = client_dropdown()
    cl = {'klient': client}

    # Default Werten aktuelles Monat
    date_format = "%Y-%m-%d"
    heute = datetime.now()
    erster_dieses_monats = datetime(heute.year, heute.month, 1)
    von = erster_dieses_monats.strftime(date_format)
    bis = heute.strftime(date_format)
    von_formatiert, bis_formatiert = eingabe_formatieren(von, bis)

    # Default Werte Jahr
    jahr = datetime.now().year
    start_datum = datetime(jahr, 1, 1)
    end_datum = datetime(jahr, 12, 31)
    start_datum_formatiert, end_datum_formatiert = eingabe_formatieren(start_datum.strftime(date_format),
                                                                       end_datum.strftime(date_format))
    if request.method == 'POST':
        # Filter auslesen
        von_ = request.form.get('von')
        bis_ = request.form.get('bis')
        mitarbeiter = request.form.get('mitarbeiter')
        klient = request.form.get('klient')

        print (klient)
        print(mitarbeiter)
        print(von_)

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

        if mitarbeiter and mitarbeiter not in ma:
            flash(f"Eingabe in Feld 'Mitarbeiter' ungültig.", "error")
            valid = False

        if klient and klient not in cl:
            flash(f"Eingabe in Feld 'Klient' ungültig.", "error")
            valid = False

        # Wenn ein Feld ungültig ist erneutes Laden der Seite mit Flash nachricht
        if not valid:
            return render_template('FGF010_view_reporting_dashboard.html', **ma, **cl)

        # Auswerten des Datums zur weiterverwendung
        if von_:
            von_date = datetime.strptime(von_, "%Y-%m-%d")
        else:
            von_date = von

        if bis_:
            bis_date = datetime.strptime(bis_, "%Y-%m-%d")
        else:
            bis_date = bis

        # Abruf mit Filter Werten
        von_formatiert, bis_formatiert = eingabe_formatieren(von_date, bis_date)

        # Ausgabe Tabellen
        kl_tabelle_gesamt = klienten_tabelle(von_formatiert, bis_formatiert, klient)
        klienten_liste = get_report_klient(von_formatiert, bis_formatiert, klient, mitarbeiter)
        ma_tabelle_gesamt = mitarbeiter_tabelle(von_formatiert, bis_formatiert, mitarbeiter)
        mitarbeiter_liste = get_report_mitarbeiter(von_formatiert, bis_formatiert, klient, mitarbeiter)
        zeiteintraege_liste = get_report_zeiteintrag(von_formatiert, bis_formatiert)

        # Ausgabe Diagramme
        maanzahl = mitarbeiter_anzahl()
        #stunden_diagramm = monatliche_gesamtstunden(von_formatiert, bis_formatiert, mitarbeiter, klient)
        #absagen_diagramm = sum_absagen_monatlich(von_formatiert, bis_formatiert, mitarbeiter, klient)
        #km_diagramm = sum_km_monatlich(von_formatiert, bis_formatiert, mitarbeiter, klient)

        return render_template('FGF010_view_reporting_dashboard.html', **ma, **cl, klienten_daten=klienten_liste,
                           mitarbeiter_daten=mitarbeiter_liste, zeiteintraege_liste=zeiteintraege_liste, klient_gesamt=kl_tabelle_gesamt, mitarbeiter_gesamt=ma_tabelle_gesamt, stundendaten=stunden_diagramm,
                           tabsagendaten=absagen_diagramm, kmdaten=km_diagramm, mazahl=maanzahl)

    kl_tabelle_gesamt = klienten_tabelle(von_formatiert, bis_formatiert, None)
    klienten_liste = get_report_klient(von_formatiert, bis_formatiert)
    ma_tabelle_gesamt = mitarbeiter_tabelle(von_formatiert, bis_formatiert, None)
    mitarbeiter_liste = get_report_mitarbeiter(von_formatiert, bis_formatiert)
    zeiteintraege_liste = get_report_zeiteintrag(von_formatiert, bis_formatiert)
    maanzahl = mitarbeiter_anzahl()
    stunden_diagramm = monatliche_gesamtstunden(start_datum_formatiert, end_datum_formatiert)
    stundendaten = [float(d) if isinstance(d, Decimal) else d for d in stunden_diagramm]
    absagen_diagramm = sum_absagen_monatlich(start_datum_formatiert, end_datum_formatiert)
    km_diagramm = sum_km_monatlich(start_datum_formatiert, end_datum_formatiert)

    print(stunden_diagramm)
    print(stundendaten)

    return render_template('FGF010_view_reporting_dashboard.html', **ma, **cl, klienten_daten=klienten_liste,
                           mitarbeiter_daten=mitarbeiter_liste, zeiteintraege_liste=zeiteintraege_liste, klient_gesamt=kl_tabelle_gesamt, mitarbeiter_gesamt=ma_tabelle_gesamt, stundendaten=stundendaten,
                           tabsagendaten=absagen_diagramm, kmdaten=km_diagramm, mazahl=maanzahl)


def eingabe_formatieren(von, bis):
    von_date = datetime.strptime(von, '%Y-%m-%d').date()
    bis_date = datetime.strptime(bis, '%Y-%m-%d').date()
    von = datetime.combine(von_date, datetime.min.time())
    bis = datetime.combine(bis_date, datetime.min.time())
    return von, bis


def stunden_addieren(data):
    total_hours = 0
    total_minutes = 0

    for _, _, _, duration in data:
        hours, minutes = duration.split(':')

        total_hours += int(hours)
        total_minutes += int(minutes)

    # Minuten in Stunden umrechnen und zur Gesamtstundenanzahl hinzufügen
    total_hours += total_minutes // 60
    total_minutes = total_minutes % 60

    return f"{total_hours:02d}:{total_minutes:02d}"


def absagen_addieren(data):
    total_absagen = 0

    for _, _, _, absagen in data:
        total_absagen += absagen

    return total_absagen


def km_addieren(data):
    total_kilometer = 0
    abrechenbare_kilometer = 0
    nicht_abrechenbare_kilometer = 0

    for _, _, _, gesamt_km, abrechenbar_km, nicht_abrechenbar_km in data:
        total_kilometer += gesamt_km
        abrechenbare_kilometer += abrechenbar_km
        nicht_abrechenbare_kilometer += nicht_abrechenbar_km

    return total_kilometer, abrechenbare_kilometer, nicht_abrechenbare_kilometer


def klienten_tabelle(von, bis, client_id):
    # Gesamt Stunden
    klstunden = sum_hours_klient_zeitspanne(von, bis)
    if client_id:
        filtered_data_s = [record for record in klstunden if record[0] == client_id]
        klient_stunden = stunden_addieren(filtered_data_s)
    else:
        klient_stunden = stunden_addieren(klstunden)

    # Gesamt Absagen
    klabsage = sum_absage_klient(von, bis)
    if client_id:
        filtered_data_a = [record for record in klabsage if record[0] == client_id]
        klient_absagen = absagen_addieren(filtered_data_a)
    else:
        klient_absagen = absagen_addieren(klabsage)

    # Gesamt KM
    klkm = sum_km_klient(von, bis)
    if client_id:
        filtered_data_k = [record for record in klkm if record[0] == client_id]
        klient_km_total, klient_km_abrechenbar, klient_km_nicht_abrechenbar = km_addieren(filtered_data_k)
    else:
        klient_km_total, klient_km_abrechenbar, klient_km_nicht_abrechenbar = km_addieren(klkm)

    return klient_km_total, klient_km_abrechenbar, klient_km_nicht_abrechenbar, klient_absagen, klient_stunden


def mitarbeiter_tabelle(von, bis, user_id):
    # Gesamt Stunden
    mastunden = sum_hours_mitarbeiter_zeitspanne(von, bis)
    if user_id:
        filtered_data_s = [record for record in mastunden if record[0] == user_id]
        mitarbeiter_stunden = stunden_addieren(filtered_data_s)
    else:
        mitarbeiter_stunden = stunden_addieren(mastunden)

    # Gesamt Absagen
    maabsage = sum_absage_mitarbeiter(von, bis)
    if user_id:
        filtered_data_a = [record for record in maabsage if record[0] == user_id]
        mitarbeiter_absagen = absagen_addieren(filtered_data_a)
    else:
        mitarbeiter_absagen = absagen_addieren(maabsage)

    # Gesamt KM
    makm = sum_km_mitarbeiter(von, bis)
    if user_id:
        filtered_data_k = [record for record in makm if record[0] == user_id]
        mitarbeiter_km_total, mitarbeiter_km_abrechenbar, mitarbeiter_km_nicht_abrechenbar = km_addieren(
            filtered_data_k)
    else:
        mitarbeiter_km_total, mitarbeiter_km_abrechenbar, mitarbeiter_km_nicht_abrechenbar = km_addieren(makm)


    return mitarbeiter_km_total, mitarbeiter_km_abrechenbar, mitarbeiter_km_nicht_abrechenbar, mitarbeiter_absagen, mitarbeiter_stunden


def mitarbeiter_anzahl():
    # aktuellen Monat und Jahr
    jetzt = datetime.now()
    aktueller_monat = jetzt.month
    aktuelles_jahr = jetzt.year

    mazahl = sum_mitarbeiter(aktueller_monat, aktuelles_jahr)
    return mazahl
