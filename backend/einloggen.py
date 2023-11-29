from flask import Flask, render_template, request, redirect, url_for, session
from databaseConnection import get_database_connection, close_database_connection
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

conn = get_database_connection()
logged_in_users = set()


def hash_password(password):
    # Hash Verschlüsselung des Passwortes
    sha1 = hashlib.sha1()
    sha1.update(password.encode('utf-8'))
    hashed_password = sha1.hexdigest()
    return hashed_password


def verify_password(password, hashed_password):
    # Überprüfung ob Passwörter übereinstimmen
    return hashlib.sha1(password.encode('utf-8')).hexdigest() == hashed_password


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Überprüfen ob alle Felder ausgefüllt wurden
        if not email or not password:
            error = "Alle Felder müssen ausgefüllt werden"
            return render_template('Einloggen.html', error=error)
        else:
            # nach Nutzerdaten in Datenbank suchen
            user = next((user for user in conn if user[email] == email), None)

        if user and email not in logged_in_users and verify_password(password, conn.person.passwort):
            # Nutzer gefunden und wird in Session hinzugefügt
            logged_in_users.add(email)
            session['user_id'] = email
            return redirect(url_for('startseite.html'))
        elif user and email in logged_in_users:
            # Nutzer ist schon angemeldet
            error = "Benutzer ist bereits eingeloggt"
            return render_template('Einloggen.html', error=error)
        elif user and user['status'] == 'locked':
            # Nutzer ist gesperrt
            error = "Anmeldung fehlgeschlagen. Wenden Sie sich an die Verwaltung"
            return render_template('Einloggen.html', error=error)
        else:
            # Nutzer nicht gefunden oder Passwort stimmt nicht
            error = "Die Zugangsdaten sind nicht korrekt."
            return render_template('Einloggen.html', error=error)

    return render_template('Einloggen.html')


close_database_connection(conn)
