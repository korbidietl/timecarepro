from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db_query import check_account_locked, validate_login, validate_email, get_role_by_email, get_person_id_by_email

login_blueprint = Blueprint("login", __name__, template_folder='templates')

logged_in_users = set()


@login_blueprint.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Überprüfen, ob alle Felder ausgefüllt wurden
        if not email or not password:
            error = "Alle Felder müssen ausgefüllt werden"
            return render_template('FNAN010_login.html', error=error)

        # wenn email in datenbank gefunden wird
        user = validate_email(email)

        if user:
            if email not in logged_in_users and validate_login(email, password):
                # Nutzer gefunden und wird in Session hinzugefügt
                logged_in_users.add(email)
                session['user_id'] = get_person_id_by_email(email)
                session['user_role'] = get_role_by_email(email)
                session['user_email'] = email
                return render_template('FAN010_home.html')
            # Passwort stimmt nicht
            elif not validate_login(email, password):
                flash("Die Zugangsdaten sind nicht korrekt.")
                return render_template('FNAN010_login.html')
            # Nutzer ist schon angemeldet
            elif email in logged_in_users:
                flash("Benutzer ist bereits eingeloggt")
                return render_template('FNAN010_login.html')
            # Nutzer ist gesperrt
            elif check_account_locked(email):
                flash("Anmeldung fehlgeschlagen. Wenden Sie sich an die Verwaltung")
                return render_template('FNAN010_login.html')

        # Nutzer nicht gefunden
        else:
            flash("Die Zugangsdaten sind nicht korrekt.")
            return render_template('FNAN010_login.html')

    return render_template('FNAN010_login.html')
