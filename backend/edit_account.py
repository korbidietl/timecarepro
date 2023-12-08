from flask import Flask, request, redirect, url_for, flash, render_template

app = Flask(__name__)
# Stellen Sie sicher, dass Sie einen geheimen Schlüssel für Flask festlegen
app.secret_key = 'IhrGeheimerSchlüssel'

@app.route('/edit_account/<int:person_id>', methods=['GET', 'POST'])
def edit_account(person_id):
    if request.method == 'POST':
        # Daten aus dem Formular holen
        lastname = request.form.get('lastname')
        firstname = request.form.get('firstname')
        # role und email sind readonly, daher werden sie nicht bearbeitet
        # Weitere Felder je nach Bedarf

        # Datenbank-Update-Logik
        try:
            update_person(person_id, lastname, firstname)
            flash('Account wurde erfolgreich bearbeitet.')
            return redirect(url_for('account_overview'))
        except Exception as e:
            flash(f'Ein Fehler ist aufgetreten: {e}')

    # Daten für die GET-Anfrage laden
    person = get_person_data(person_id)  # Ihre Funktion zum Abrufen der Personendaten
    return render_template('edit_account.html', person=person)

def update_person(person_id, lastname, firstname):
    # Logik zur Aktualisierung der Person in der Datenbank
    # Verwenden Sie hier Ihre Datenbankverbindung und -abfrage
    pass

def get_person_data(person_id):
    # Logik zum Abrufen der Personendaten aus der Datenbank
    # Verwenden Sie hier Ihre Datenbankverbindung und -abfrage
    return {
        'id': person_id,
        'lastname': 'Mustermann',
        'firstname': 'Max',
        'role': 'Mitarbeiter',
        'email': 'max.mustermann@example.com'
    }

if __name__ == '__main__':
    app.run(debug=True)
