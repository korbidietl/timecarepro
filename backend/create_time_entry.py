from flask import Flask, request, redirect, url_for
import mysql.connector
from db_query import add_zeintrag, add_fahrt
from datetime import datetime

app = Flask(__name__)

@app.route('/submit_time_entry', methods=['POST'])
def submit_arbeitsstunden():
    # Eingabedaten aus dem Formular holen
    datum = request.form.get('datum')
    start_zeit = request.form.get('startZeit')
    end_zeit = request.form.get('endZeit')
    kilometer = request.form.get('kilometer')
    klient_id = request.form.get('klient')  # Nehmen wir an, dass dies die ID ist
    beschreibung = request.form.get('beschreibung')
    interne_notiz = request.form.get('interneNotiz')
    unterschrift_klient
    unterschrift_mitarbeiter
    # hier müssen noch unterschriften rein

    # Konvertiere Datum und Uhrzeit in ein datetime-Objekt
    start_datetime = datetime.strptime(f"{datum} {start_zeit}", '%Y-%m-%d %H:%M')
    end_datetime = datetime.strptime(f"{datum} {end_zeit}", '%Y-%m-%d %H:%M')

    # Füge neuen Zeiteintrag hinzu und erhalte die ID
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
