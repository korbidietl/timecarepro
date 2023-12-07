from flask import Flask, request, redirect, url_for, render_template
from db_query import add_zeiteintrag, add_fahrt, check_for_overlapping_zeiteintrag
from datetime import datetime

app = Flask(__name__)

@app.route('/create_time_entry', methods=['POST'])
def submit_arbeitsstunden():
    # Eingabedaten aus dem Formular holen
    datum = request.form.get('datum')
    start_zeit = request.form.get('startZeit')
    end_zeit = request.form.get('endZeit')
    kilometer = request.form.get('kilometer')
    # da müssen wir uns noch überlegen, wie das am besten sinn macht
    # weil klient name kann ja doppelt sein, aber das dropdown soll ja keine id anzeigen
    # wie erkennt man aber im dropdown welcher max mustermann der richtige ist?
    klient_id = request.form.get('klient')
    beschreibung = request.form.get('beschreibung')
    interne_notiz = request.form.get('interneNotiz')
    # hier müssen noch unterschriften rein
    unterschrift_klient
    unterschrift_mitarbeiter

    # Konvertiere Datum und Uhrzeit in ein datetime-Objekt
    start_datetime = datetime.strptime(f"{datum} {start_zeit}", '%Y-%m-%d %H:%M')
    end_datetime = datetime.strptime(f"{datum} {end_zeit}", '%Y-%m-%d %H:%M')

    # Prüft ob, Startzeitpunkt vor Endzeitpunkt liegt.
    if start_datetime >= end_datetime:
        return render_template("create_time_entry.html", error="Endzeitpunkt muss nach Startzeitpunkt sein.")

    # prüft auf überschneidung einer bestehenden eintragung in der datenbank
    elif check_for_overlapping_zeiteintrag(time_id,klient_id, start_zeit, end_zeit):
        # überschneidungs funktion
        return /FS030/

    # Füge neuen Zeiteintrag hinzu und erhalte die ID
    else:
        zeiteintrag_id = add_zeiteintrag(datum, start_datetime, end_datetime, beschreibung, interne_notiz, unterschrift_klient, unterschrift_mitarbeiter)

        # Falls Kilometer angegeben, füge Fahrt hinzu
        if kilometer:
            add_fahrt(zeiteintrag_id, kilometer)

    # Weiterleitung zurück zur Übersicht der abgelegten Stunden
    return redirect(url_for('arbeitsleistung_uebersicht'))

# Ersetze 'arbeitsleistung_uebersicht' mit der tatsächlichen Route für die Übersicht
@app.route('/see_time_entry')
def arbeitsleistung_uebersicht():
    # Implementierung der Übersichtsansicht
    pass

if __name__ == '__main__':
    app.run(debug=True)
