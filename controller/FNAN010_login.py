from flask import Blueprint, render_template, request, session, flash, url_for, redirect
from model.person import validate_login, check_account_locked, validate_email, get_role_by_email, \
    get_person_id_by_email, is_password_required

login_blueprint = Blueprint("login", __name__)

logged_in_users = set()


@login_blueprint.route('/', methods=['GET', 'POST'])
def login():
    # Rückleitung bei unerlaubter Seite
    session['secure_url'] = url_for('login.login')

    if request.method == 'POST':
        # Auslesen aus Forumlar
        email = request.form['email']
        password = request.form['password']
        session['ueberschneidung'] = 0

        # Überprüfen, ob alle Felder ausgefüllt wurden
        if not email or not password:
            flash("Alle Felder müssen ausgefüllt werden")
            return render_template('FNAN010_login.html')

        # Nutzer in Datenbank suchen
        user = validate_email(email)

        # Nutzer gefunden
        if user:
            # Nutzer ist gesperrt
            if check_account_locked(email):
                flash("Anmeldung fehlgeschlagen. Wenden Sie sich an die Verwaltung.")
                return render_template('FNAN010_login.html')

            # Nutzer ist schon angemeldet
            elif email in logged_in_users:
                flash("Benutzer ist bereits eingeloggt.")
                return render_template('FNAN010_login.html')

            # Passwort ist falsch
            elif not validate_login(email, password):
                flash("Die Zugangsdaten sind nicht korrekt.")
                return render_template('FNAN010_login.html')

            # Einloggen Nutzer
            elif email not in logged_in_users and validate_login(email, password):
                logged_in_users.add(email)
                session['user_id'] = get_person_id_by_email(email)
                session['user_email'] = email
                session['user_role'] = get_role_by_email(email)

                # Weiterleitung wenn Nutzer Passwort ändern muss
                if is_password_required(email):
                    return redirect(url_for('password_change.change_password'))
                return redirect(url_for('home.home'))

        # Nutzer nicht gefunden
        else:
            flash("Die Zugangsdaten sind nicht korrekt.")
            return render_template('FNAN010_login.html')

    return render_template('FNAN010_login.html')
