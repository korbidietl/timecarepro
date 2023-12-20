from datetime import datetime

from flask import Blueprint, render_template, url_for, request, flash, redirect
from db_query import mitarbeiter_dropdown, client_dropdown, sum_mitarbeiter, sum_hours_mitarbeiter, sum_hours_klient, \
    sum_absage_mitarbeiter, sum_absage_klient, sum_km_mitarbeiter, sum_km_klient, kostentraeger_dropdown

reporting_dachboard_blueprint = Blueprint('view_reporting_dashboard', __name__)


@reporting_dachboard_blueprint.route('/reporting_dashboard', methods={'GET', 'POST'})
def reporting_dashboard():
    mitarbeiter = mitarbeiter_dropdown()
    ma = {'mitarbeiter': mitarbeiter}

    client = client_dropdown()
    cl = {'klient': client}

    if request.method == 'POST':
        # Filter auslesen
        von = request.form.get('von')
        bis = request.form.get('bis')
        mitarbeiter = request.form.get('mitarbeiter')
        klient = request.form.get('klient')

        # Überprüfung Eingaben
        date_format = "%d.%m.%Y"
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

        if mitarbeiter not in ma:
            flash(f"Eingabe in Feld 'Mitarbeiter' ungültig.", "error")
            valid = False

        if klient not in cl:
            flash(f"Eingabe in Feld 'Klient' ungültig.", "error")
            valid = False

        # Wenn ein Feld ungültig ist erneutes Laden der Seite mit Flash nachricht
        if not valid:
            return render_template('FGF010_view_reporting_dashboard.html', **ma, **cl)

        # Auswerten des Datums zur weiterverwendung
        if von:
            von_date = datetime.strptime(von, "%d.%m.%Y")
            von_day, von_month, von_year = von_date.day, von_date.month, von_date.year

        if bis:
            bis_date = datetime.strptime(bis, "%d.%m.%Y")
            bis_day, bis_month, bis_year = bis_date.day, bis_date.month, bis_date.year

        anzeigen(von_day, von_month, von_year, bis_day, bis_month, bis_year)

    # Abruf mit aktuellem Monat
    heute = datetime.now()
    erster_dieses_monats = datetime(heute.year, heute.month, 1)

    von_day = erster_dieses_monats.day
    von_month = erster_dieses_monats.month
    von_year = erster_dieses_monats.year
    bis_day = heute.day
    bis_month = heute.month
    bis_year = heute.year
    anzeigen(von_day, von_month, von_year, bis_day, bis_month, bis_year)

    return render_template('FGF010_view_reporting_dashboard.html', **ma, **cl)


def anzeigen(von_day, von_month, von_year, bis_day, bis_month, bis_year):
    # Tabelle Mitarbeiter
    mastunden = sum_hours_mitarbeiter(month, year)
    maabsagen = sum_absage_mitarbeiter(month, year)
    # abrechenbare km und nicht-abrechenbare km
    makm = sum_km_mitarbeiter(month, year)
    # Tabelle Mitarbeiter einbinden

    # Tabelle Klient
    klstunden = sum_hours_klient(month, year)
    klabsage = sum_absage_klient(month, year)
    # km abrechenbar und nicht-abrechenbar
    klkm = sum_km_klient(month, year)
    # Tabelle Klient einbinden

    # Tabelle Zeiteinträge

    # tabellen_daten = db_abruf_funktion()

    # Darstellungen
    mazahl = sum_mitarbeiter(month, year)
    stundendaten = get_stundendaten_fuer_jeden_monat()

    return render_template(tabellen_daten=tabellen_daten, mastunden=mastunden, maabsagen=maabsagen, makm=makm,
                           klstunden=klstunden, klabsage=klabsage, klkm=klkm, mazahl=mazahl, stundendaten=stundendaten )
