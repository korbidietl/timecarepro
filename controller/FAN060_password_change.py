from flask import render_template, request, Blueprint, session, flash, redirect, url_for
from model.person import validate_login, set_password_mail, set_password_required_false, get_firstname_by_email, \
    get_lastname_by_email
from model.mailserver_connection import send_email

password_change_blueprint = Blueprint("password_change", __name__)


def validate_password(password):
    # Überprüft, ob das Passwort den Anforderungen entspricht (z.B. Länge)
    return len(password) >= 10


def send_email_passwort_change(email, firstname, lastname):
    subject = "Ihr neues Passwort"
    body = (f"Sehr geehrte/r {firstname} {lastname}, \n\n"
            f"Sie haben ihr Passwort erfolgreich geändert. \n\n"
            f"Mit freundlichen Grüßen\n"
            f"Ihr TimeCare Pro-Team")
    send_email(email, subject, body)


@password_change_blueprint.route('/password_change', methods=['POST', 'GET'])
def change_password():
    if 'user_id' in session:
        # Rückleitung bei unerlaubter Seite
        session['secure_url'] = url_for('password_change.change_password')

        if request.method == "POST":

            current_password = request.form["current_password"]
            new_password = request.form["new_password"]
            confirm_password = request.form["confirm_password"]

            # Peröhnliche Daten für Email
            email = session.get('user_email')
            firstname = get_firstname_by_email(email)
            lastname = get_lastname_by_email(email)

            # Prüfen, ob alle Felder ausgefüllt sind
            if not current_password or not new_password or not confirm_password:
                flash("Alle Felder müssen ausgefüllt werden.")
                return render_template("FAN060_password_change.html")

            # Prüfen, ob die neuen Passwörter übereinstimmen
            elif new_password != confirm_password:
                flash("Die Felder „Neues Passwort“ und „Neues Passwort bestätigen“ müssen übereinstimmen.")
                return render_template("FAN060_password_change.html")

            # Prüfen, ob das neue Passwort den Anforderungen entspricht
            elif not validate_password(new_password):
                flash("Das neue Passwort muss mindestens 10 Zeichen enthalten.")
                return render_template("FAN060_password_change.html")

            # Überprüfen, ob das aktuelle Passwort korrekt ist
            elif not validate_login(session['user_email'], current_password):
                flash("Das aktuelle Passwort ist nicht korrekt.")
                return render_template("FAN060_password_change.html")

            # Aktualisieren des Passworts
            else:
                set_password_required_false(email)
                set_password_mail(email, new_password)
                send_email_passwort_change(email, firstname, lastname)
                flash(
                    "Das Passwort wurde erfolgreich geändert und eine Bestätigungs-Mail versendet.",
                    "success")

                return redirect(url_for('home.home'))

        return render_template("FAN060_password_change.html")

    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))
