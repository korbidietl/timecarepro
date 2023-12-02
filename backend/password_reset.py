from flask import Blueprint, render_template, request
import random
import string
import smtplib
from email.mime.text import MIMEText
from db_query import validate_email, check_account_locked, set_password, set_password_required_true, get_lastname_by_email

password_reset_blueprint = Blueprint("password_reset", __name__)


# Neues Passwort wird erzeugt
def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))


def send_email(email, lastname, new_password):
    subject = "Ihr neues Passwort"
    body = (f"Sehr geehrte/r Frau/Mann {lastname}, \n\n"
            f"Ihr Passwort wurde erfolgreich zurückgesetzt. "
            f"Das automatisch generierte Passwort ist: {new_password} \n"
            f"Bitte ändern Sie dieses Passwort schnellstmöglich.\n\n"
            f"Mit freundlichen Grüßen\n"
            f"Ihr TimeCare Pro-Team")
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'resetyourpasswort@timecarepro.de'
    msg['To'] = email

    with smtplib.SMTP('132.231.36.210', 1103) as smtp:
        smtp.starttls()
        smtp.login('mailhog_grup3', 'Uni75Winfo17Master')
        smtp.sendmail('resetyourpassword@timecarepro.de', [email], msg.as_string())


@password_reset_blueprint.route('/password_reset', methods=['POST'])
def passwordreset():
    print("Hello")
    if request.method == "POST":
        email = request.form["email"]
        user = validate_email(email)

        # Es wurde keine E-mail übergeben
        if not email:
            error = "Geben Sie für das Zurücksetzen des Passworts zuerst Ihre E-Mail-Adresse ein."
            return render_template("password_reset.html", error=error)

        else:
            if user:
                lastname = get_lastname_by_email(email)
                locked = check_account_locked(email)

                if locked:
                    # Überprüfung ob Nutzer gesperrt ist
                    return render_template("password_reset.html")
                else:
                    # Neues Passwort generieren, abspeichern und Passwort erzwingen auf True setzen
                    new_password = generate_random_password()
                    set_password(email, new_password)
                    set_password_required_true(email)
                    # E-Mail senden
                    send_email(email, lastname, new_password)

                    return render_template('login.html', email=email,
                                           success_message="Ein neues Passwort wurde an die "
                                                           "angegebene E-Mail-Adresse "
                                                           "versendet.")
            else:
                # keine E-mail in der Datenbank gefunden
                return render_template('login.html')
