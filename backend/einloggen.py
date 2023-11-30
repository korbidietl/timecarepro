from flask import Blueprint, render_template, request, redirect, url_for, session
from db_query import get_user_by_email  # , get_password_for_user, get_role_for_user(email), get_locked_status(email)
from datetime import datetime, timedelta
import hashlib

einloggen_blueprint = Blueprint("einloggen", __name__)

logged_in_users = set()


def hash_password(password):
    # Hash Verschlüsselung des Passwortes
    sha1 = hashlib.sha1()
    sha1.update(password.encode('utf-8'))
    hashed_password = sha1.hexdigest()
    return hashed_password


def verify_password(password, hashed_password):
    # Überprüfung ob Passwörter übereinstimmen
    encrypted_password = hash_password(password)
    return encrypted_password == hashed_password


@einloggen_blueprint.route('/', methods=['GET', 'POST'])
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
            user = get_user_by_email(email)
            if user:
                password_user = get_password_for_user(email)
                role_user = get_role_for_user(email)
                locked_status = get_locked_status(email)

                if user and email not in logged_in_users and verify_password(password, password_user)
                    # Nutzer gefunden und wird in Session hinzugefügt
                    logged_in_users.add(email)
                    session['user_id'] = email
                    session['last_activity'] = datetime.now()
                    session['user_role'] = role_user
                    return redirect(url_for('startseite.html'))
                elif user and email in logged_in_users:
                    # Nutzer ist schon angemeldet
                    error = "Benutzer ist bereits eingeloggt"
                    return render_template('Einloggen.html', error=error)
                elif locked_status == 0:
                    # Nutzer ist gesperrt
                    error = "Anmeldung fehlgeschlagen. Wenden Sie sich an die Verwaltung"
                    return render_template('Einloggen.html', error=error)
                else:
                    # Passwort stimmt nicht
                    error = "Die Zugangsdaten sind nicht korrekt."
                    return render_template('Einloggen.html', error=error)

            else:
                # Nutzer nicht gefunden
                error = "Die Zugangsdaten sind nicht korrekt."
                return render_template('Einloggen.html', error=error)


@einloggen_blueprint.route('/Menüleiste')
def startseite():
    if 'last_activity' in session:
        last_activity = session['last_activity']
        if datetime.now() - last_activity > timedelta(minutes=30):  # Setze die Inaktivitätszeit auf 30 Minuten
            session.clear()  # Lösche die Sitzung, um den Benutzer auszuloggen
            return redirect(url_for('.login'))  # Nutze den Blueprint-Prefix

    return render_template('Menüleiste.html', role=session.get('user_role'))
