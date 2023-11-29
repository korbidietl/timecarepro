import hashlib
import smtplib
import random
import string
import mysql.connector
from email.mime.text import MIMEText

from flask import request, app

from databaseConnection import get_database_connection

# Ersetzen Sie 'localhost', 'username', 'password' und 'database' durch Ihre tatsächlichen Datenbank-Informationen
connection = get_database_connection()
cursor = connection.cursor()


# Hash-Funktion für Passwörter
def hash_password(password):
    return hashlib.sha1(password.encode()).hexdigest()


# Passwort-Rücksetzung-Funktion
def password_reset(email):
    # Abfrage der Datenbank nach der E-Mail-Adresse
    cursor.execute("SELECT * FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()

    if result:
        # Erzeugen eines neuen Passworts, falls eine E-Mail-Adresse gefunden wurde
        new_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))

        # Passwort hashen und in der Datenbank aktualisieren
        hashed_password = hash_password(new_password)
        cursor.execute("UPDATE person SET passwort = %s WHERE email = %s", (hashed_password, email))
        connection.commit()

        # E-Mail senden
        subject = "Ihr neues Passwort"
        body = f"Hallo, Ihr neues Passwort lautet: {new_password}"
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = 'resetyourpasswort@timecarepro.de'
        msg['To'] = email
        smtp = smtplib.SMTP('132.231.36.210', 1103)
        smtp.starttls()
        smtp.login('mailhog_grup3', 'Uni75Winfo17Master')
        smtp.sendmail('resetyourpassword@timecarepro.de', email, msg.as_string())
        smtp.quit()

        return "Ein neues Passwort wurde an {} gesendet".format(email)
    else:
        return "Passwort konnte nicht zurückgesetzt werden"


# Die Route, die die Anfrage vom Benutzer akzeptiert
@app.route('/password_reset', methods=['POST'])
def handle_password_reset():
    email = request.form['email']
    result = password_reset(email)
    return result
