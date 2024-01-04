from datetime import datetime

from flask import Blueprint, render_template, url_for, request, flash, redirect
from db_query import mitarbeiter_dropdown, client_dropdown, sum_mitarbeiter, sum_hours_mitarbeiter, sum_hours_klient, \
    sum_absage_mitarbeiter, sum_absage_klient, sum_km_mitarbeiter, sum_km_klient, get_report_zeiteintrag, \
    get_report_mitarbeiter, get_report_klient

reporting_dachboard_blueprint = Blueprint('view_reporting_dashboard', __name__)


@reporting_dachboard_blueprint.route('/reporting_dashboard', methods={'GET', 'POST'})
def reporting_dashboard():
    # Dropdown Felder
    mitarbeiter = mitarbeiter_dropdown()
    ma = {'mitarbeiter': mitarbeiter}

    client = client_dropdown()
    cl = {'klient': client}

    # Default Datumswerte
    date_format = "%Y-%m-%d"
    heute = datetime.now()
    erster_dieses_monats = datetime(heute.year, heute.month, 1)

    von = erster_dieses_monats.strftime(date_format)
    bis = heute.strftime(date_format)

    if request.method == 'POST':
        # Filter auslesen
        von = request.form.get('von')
        bis = request.form.get('bis')
        mitarbeiter = request.form.get('mitarbeiter')
        klient = request.form.get('klient')

        # Überprüfung Eingaben
        valid = True

        try:
            if von:
                datetime.strptime(von, date_format)
        except ValueError:
            flash(f"Eingabe in Feld 'von' ungültig.", "error")
            valid = False

        try:
            if bis:
                datetime.strptime(bis, date_format)
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
        if von:
            von_date = datetime.strptime(von, "%d.%m.%Y").strftime('%Y-%m-%d')
        else:
            von_date = von

        if bis:
            bis_date = datetime.strptime(bis, "%d.%m.%Y").strftime('%Y-%m-%d')
        else:
            bis_date = bis

        # Abruf mit Filter Werten
        daten= anzeigen(von_date, bis_date)
        return render_template('FGF010_view_reporting_dashboard.html', **ma, **cl, **daten)

    # Abruf mit Default Werten
    daten= anzeigen(von, bis)
    return render_template('FGF010_view_reporting_dashboard.html', **ma, **cl, **daten)


def anzeigen(von, bis):
    # Tabelle Mitarbeiter
    mastunden = sum_hours_mitarbeiter(von, bis)
    maabsagen = sum_absage_mitarbeiter(von, bis)
    # abrechenbare km und nicht-abrechenbare km
    makm = sum_km_mitarbeiter(von, bis)
    mitarbeiter_liste = get_report_mitarbeiter(von, bis)

    # Tabelle Klient
    klstunden = sum_hours_klient(von, bis)
    klabsage = sum_absage_klient(von, bis)
    # km abrechenbar und nicht-abrechenbar
    klkm = sum_km_klient(von, bis)
    klienten_liste = get_report_klient(von, bis)

    # Tabelle Zeiteinträge

    zeiteintraege_liste = get_report_zeiteintrag(von, bis)

    # Diagramme
    mazahl = sum_mitarbeiter(von, bis)

    stundendaten =  []
    kmdaten = []
    tabsagendaten= []

    return {
        'zeiteintraege_liste': zeiteintraege_liste,
        'mitarbeiter_liste': mitarbeiter_liste,
        'klienten_liste': klienten_liste,
        'mastunden': mastunden,
        'maabsagen': maabsagen,
        'makm': makm,
        'klstunden': klstunden,
        'klabsage': klabsage,
        'klkm': klkm,
        'mazahl': mazahl,
        'stundendaten': stundendaten,
        'kmdaten': kmdaten,
        'tabsagendaten': tabsagendaten
    }