from flask import Flask, render_template, request, session
import db_query

app = Flask(__name__)

@app.route('/mitarbeiter', methods=['GET', 'POST'])
def mitarbeiter():
    if request.method == 'POST':
        gewaehlter_zeitraum = request.form['zeitraum']
    else:
        gewaehlter_zeitraum = None  # oder aktuellen Monat setzen

    # Logik, um die benötigten Daten aus der Datenbank zu holen
    # Beispiel: mitarbeiter = db_query.get_mitarbeiter_data(gewaehlter_zeitraum)

    # Fehlerbehandlung, wenn keine Mitarbeiter gefunden werden
    if not mitarbeitern:
        error_message = "Keine Mitarbeiter gefunden."
        return render_template('mitarbeiter.html', error_message=error_message)

    return render_template('mitarbeiter.html', mitarbeitern=mitarbeitern)

if __name__ == '__main__':
    app.run(debug=True)
