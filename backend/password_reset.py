from flask import render_template, request, app
import random
import string
import smtplib
from einloggen import hash_password
from email.mine.text import MINEText
from databaseConnection import get_database_connection

connection = get_database_connection()
cursor = connection.cursor()

@app.route('/password_reset', methods=['POST'])
def handle_password_reset():
    email = request.form['email']
    result = password_reset(email)
    return result

# Passwort wird erzeugt
def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))


def reset_password_logic(email):
    # Es wurde keine E-mail übergeben
    if not email:
        error = "Geben Sie für das Zurücksetzen des Passworts zuerst Ihre E-Mail-Adresse ein."
        return render_template("password_reset.html")

    # Überprüfung ob in der Datenbank diese E-Mail hinterlegt ist
    cursor.execute("SELECT * FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()

    if result:
        # Überprüfung ob Nutzer gesperrt ist
        if person.get("status") == "locked":
            error = "Passwortänderung fehlgeschlagen. Wenden Sie sich an die Verwaltung."
            return render_template("password_reset.html", error=error)
        else:
            new_password = generate_random_password()
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

            return render_template('Einloggen.html', email=email)
    else:
        # keine E-mail in der Datenbank gefunden
        return render_template('Einloggen.html')
