from flask import Flask, render_template, request, session
from db_query import account_table
import db_query

app = Flask(__name__)

@app.route('/mitarbeiter', methods=['GET', 'POST'])
def mitarbeiter():
    if request.method == 'POST':

        monat = request.form['zeitraum']

        mitarbeiterliste = account_table(monat)

    # Fehlerbehandlung, wenn keine Mitarbeiter gefunden werden
    if not mitarbeiterliste:
        error_message = "Keine Mitarbeiter gefunden."
        return render_template('show_employee_table.html', error_message=error_message)

    return render_template('show_employee_table.html', mitarbeitern=mitarbeitern)

if __name__ == '__main__':
    app.run(debug=True)
