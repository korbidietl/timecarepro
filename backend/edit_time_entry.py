# Haupt-Flask-Datei (z.B. app.py)
from flask import Flask, render_template, request, redirect, url_for, session
from db_query import fetch_time_entry_data, edit_zeiteintrag

app = Flask(__name__)

@app.route('/edit_time_entry/<zeiteintrag_id>', methods=['GET', 'POST'])
def edit_time_entry(zeiteintrag_id):
    if request.method == 'POST':
        # Annahme, dass die Formulardaten die erforderlichen Werte enthalten
        start_time = request.form.get('startZeit')
        end_time = request.form.get('endZeit')
        # Anpassen für Unterschriften und andere Felder nach Bedarf
        unterschrift_mitarbeiter = request.form.get('unterschriftMitarbeiter')
        unterschrift_klient = request.form.get('unterschriftKlient')

        # Aktualisieren des Zeiteintrags
        edit_zeiteintrag(zeiteintrag_id, start_time, end_time, unterschrift_mitarbeiter, unterschrift_klient)

        # Weiterleiten nach dem Aktualisieren
        return redirect(url_for('irgendeine_weitere_route'))

    # Wenn die Methode GET ist, lade die Seite zum Bearbeiten
    zeiteintrag_data, fahrten_data = fetch_time_entry_data(zeiteintrag_id)
    return render_template('edit_time_entry.html', zeiteintrag=zeiteintrag_data, fahrten=fahrten_data)

if __name__ == '__main__':
    app.run(debug=True)

