from flask import Flask, render_template, request
import random
import string
import smtplib
import hashlib
from email.mime.text import MIMEText
from databaseConnection import get_database_connection

conn = get_database_connection()
cursor = conn.cursor()

app = Flask(__name__)


@app.route('/password_reset', methods=['POST'])
def handle_password_reset():
    email = request.form['email']
    result = password_reset(email)
    return result


# Neues Passwort wird erzeugt
def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))


def hash_password(password):
    # Hash Verschlüsselung des Passwortes
    sha1 = hashlib.sha1()
    sha1.update(password.encode('utf-8'))
    hashed_password = sha1.hexdigest()
    return hashed_password


def password_reset(email):
    try:
        # Es wurde keine E-mail übergeben
        if not email:
            error = "Geben Sie für das Zurücksetzen des Passworts zuerst Ihre E-Mail-Adresse ein."
            return render_template("password_reset.html", error=error)

        # Überprüfung ob in der Datenbank diese E-Mail hinterlegt ist
        cursor.execute("SELECT * FROM person WHERE email = %s", (email,))
        result = cursor.fetchone()

        if result:
            person_nachname = result[2]
            person_sperre = result[9]

            if not person_sperre == 0:
                # Überprüfung ob Nutzer gesperrt ist
                return render_template("password_reset.html")
            else:
                new_password = generate_random_password()
                hashed_password = hash_password(new_password)
                cursor.execute("UPDATE person SET passwort = %s WHERE email = %s", (hashed_password, email))
                connection.commit()

                # E-Mail senden
                subject = "Ihr neues Passwort"
                body = (f"Sehr geehrte/r Frau/Mann {person_nachname}, \n\n"
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

                return render_template('Einloggen.html', email=email, success_message="Ein neues Passwort wurde an die "
                                                                                      "angegebene E-Mail-Adresse "
                                                                                      "versendet.")
        else:
            # keine E-mail in der Datenbank gefunden
            return render_template('Einloggen.html')

    finally:
        connection.close()
