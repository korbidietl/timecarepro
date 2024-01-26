from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import random
import string
import smtplib
from email.mime.text import MIMEText
from model.person import check_account_locked, set_password_mail, validate_email, set_password_required_true, \
    get_firstname_by_email, get_lastname_by_email

password_reset_blueprint = Blueprint("password_reset", __name__)


# Neues Passwort wird erzeugt
def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))


# Versand Email
def send_email(email, subject, body):
    msg = MIMEText(body)

    msg['Subject'] = subject
    msg['From'] = 'resetyourpasswort@timecarepro.de'
    msg['To'] = email

    with smtplib.SMTP('132.231.36.210', 1103) as smtp:
        smtp.login('mailhog_grup3', 'Uni75Winfo17Master')
        smtp.sendmail('resetyourpassword@timecarepro.de', [email], msg.as_string())


# Nachricht wird erzeugt
def send_email_passwort_reset(email, firstname, lastname, new_password):
    subject = "Ihr neues Passwort"
    body = (f"Sehr geehrte/r {firstname} {lastname}, \n\n"
            f"Sie haben Ihr Passwort erfolgreich zurückgesetzt.\n "
            f"Das automatisch generierte Passwort ist: {new_password} \n"
            f"Bitte ändern Sie dieses Passwort schnellstmöglich.\n\n"
            f"Freundliche Grüße\n"
            f"Ihr TimeCare Pro-Team")
    send_email(email, subject, body)


@password_reset_blueprint.route('/password_reset', methods=['POST', 'GET'])
def passwordreset():
    # Rückleitung bei unerlaubter Seite
    session['secure_url'] = url_for('password_reset.passwordreset')

    if request.method == "POST":
        email = request.form["email"]

        # Keine E-Mail übergeben
        if not email:
            flash("Geben Sie für das Zurücksetzen des Passworts zuerst Ihre E-Mail-Adresse ein.")
            return render_template("FNAN020_password_reset.html")

        # Nutzer in Datenbank suchen
        user = validate_email(email)

        if user:
            # Persöhnliche Daten für Email
            lastname = get_lastname_by_email(email)
            firstname = get_firstname_by_email(email)

            # Überprüfung ob Nutzer gesperrt
            locked = check_account_locked(email)
            if locked:
                # Nutzer ist gesperrt
                flash("Passwort zurücksetzen fehlgeschlagen. Wenden Sie sich an die Verwaltung")
                return render_template("FNAN020_password_reset.html")
            else:
                # Passwort zurücksetzen
                new_password = generate_random_password()
                set_password_mail(email, new_password)
                set_password_required_true(email)

                # E-Mail senden
                send_email_passwort_reset(email, firstname, lastname, new_password)
                flash("Ein neues Passwort wurde an die angegebene E-Mail-Adresse versendet, falls diese im System "
                      "vorhanden ist.", "success")

                # Weiterleitung zum Login
                return redirect(url_for('login.login'))
        else:
            # kein Nutzer gefunden
            return redirect(url_for('login.login'))

    return render_template('FNAN020_password_reset.html')
