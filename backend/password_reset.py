from flask import render_template
import random
import string
from einloggen import hash_password


def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))


def reset_password_logic(email):
    # Es wurde keine E-mail übergeben
    if not email:
        error = "Geben Sie für das Zurücksetzen des Passworts zuerst Ihre E-Mail-Adresse ein."
        return render_template("password_reset.html")

    # Überprüfung ob in der Datenbank diese E-Mail hinterlegt ist
    user = next((user for user in conn if user['email'] == email), None)

    if user:
        # Überprüfung ob Nutzer gesperrt ist
        if user.get("status") == "locked":
            error = "Passwortänderung fehlgeschlagen. Wenden Sie sich an die Verwaltung."
            return render_template("password_reset.html", error=error)
        else:
            new_password = generate_random_password()
            hashed_password = hash_password(new_password)
            user['password'] = hashed_password
            return render_template('Einloggen.html', email=email)
    else:
        # keine E-mail in der Datenbank gefunden
        return render_template('Einloggen.html')
