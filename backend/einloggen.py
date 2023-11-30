from flask import Blueprint, render_template, request, redirect, url_for, session
from db_query import get_user_by_email, check_account_locked, validate_login, email_exists, get_role_for_user,  # , get_password_for_user
from datetime import datetime, timedelta
import hashlib

einloggen_blueprint = Blueprint("einloggen", __name__)

logged_in_users = set()

# evtl diese methoden "public" machen. werden immer wieder verwendet --> redundanter code
def hash_password(password):
    # Hash Verschlüsselung des Passwortes
    sha1 = hashlib.sha1()
    sha1.update(password.encode('utf-8'))
    hashed_password = sha1.hexdigest()
    return hashed_password

# gleiches spiel wie bei hash_password
def verify_password(password, hashed_password):
    # Überprüfung ob Passwörter übereinstimmen
    encrypted_password = hash_password(password)
    return encrypted_password == hashed_password


# beim log-in prozess sollte die user id als session id gespeichert werden !!
# diese muss dann file übergreifend abrufbar sein.
# bsp.: beim log-in wird user id ermittelt
# --> diese wird bei passwort_change erneut gebraucht, damit der user nicht wieder seine email eingeben muss

@einloggen_blueprint.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Überprüfen ob alle Felder ausgefüllt wurden
        if not email or not password:
            error = "Alle Felder müssen ausgefüllt werden"
            return render_template('Einloggen.html', error=error)

        # wenn email in datenbank gefunden wird
        elif email_exists(email):

            # Nutzer gefunden und wird in Session hinzugefügt
            if user and email not in logged_in_users and validate_login(email, password)
                logged_in_users.add(email)
                session['user_id'] = email
                # wozu ist die last activity in der session relevant??
                session['last_activity'] = datetime.now()
                session['user_role'] = get_role_for_user(email)
                return redirect(url_for('startseite.html'))
            # Nutzer ist schon angemeldet
            elif user and email in logged_in_users:
                error = "Benutzer ist bereits eingeloggt"
                return render_template('Einloggen.html', error=error)
            # Nutzer ist gesperrt
            elif check_account_locked(email):
                error = "Anmeldung fehlgeschlagen. Wenden Sie sich an die Verwaltung"
                return render_template('Einloggen.html', error=error)
            # Passwort stimmt nicht
            else:
                error = "Die Zugangsdaten sind nicht korrekt."
                return render_template('Einloggen.html', error=error)

        # Nutzer nicht gefunden
        else:
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
