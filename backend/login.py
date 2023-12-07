from flask import Blueprint, render_template, request, redirect, url_for, session
from db_query import check_account_locked, validate_login, validate_email, get_role_by_email, get_person_id_by_email


login_blueprint = Blueprint("login", __name__)

logged_in_users = set()


# @app.route("/login", methods=['POST'])
@login_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Überprüfen, ob alle Felder ausgefüllt wurden
        if not email or not password:
            error = "Alle Felder müssen ausgefüllt werden"
            return render_template('login.html', error=error)

        # wenn email in datenbank gefunden wird
        user = validate_email(email)

        if user:
            if user and email not in logged_in_users and validate_login(email, password):
                # Nutzer gefunden und wird in Session hinzugefügt
                logged_in_users.add(email)
                session['user_id'] = get_person_id_by_email(email)
                session['user_role'] = get_role_by_email(email)
                session['user_email'] = email
                return redirect(url_for('home.html'))
            # Nutzer ist schon angemeldet
            elif user and email in logged_in_users:
                error = "Benutzer ist bereits eingeloggt"
                return render_template('login.html', error=error)
            # Nutzer ist gesperrt
            elif check_account_locked(email):
                error = "Anmeldung fehlgeschlagen. Wenden Sie sich an die Verwaltung"
                return render_template('login.html', error=error)
            # Passwort stimmt nicht
            else:
                error = "Die Zugangsdaten sind nicht korrekt."
                return render_template('login.html', error=error)

        # Nutzer nicht gefunden
        else:
            error = "Die Zugangsdaten sind nicht korrekt."
            return render_template('login.html', error=error)

# @einloggen_blueprint.route('/Menüleiste')
# def startseite():
# return render_template('navbar.html', role=session.get('user_role'))
