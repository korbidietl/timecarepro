from flask import render_template, request
import hashlib
from db_query import get_user_by_id, update_password_for_user

password_reset_blueprint = Blueprint("password_reset", __name__)


# funktion doppelt sich mit hash_password aus password_reset.py
# ich weiß nicht ob sie trotzdem doppelt aufgeführt werden muss
def hash_password(password):
    sha1 = hashlib.sha1()
    sha1.update(password.encode('utf-8'))
    return sha1.hexdigest()

# ich habe jetzt mal eine minimale passwort länge von 8 festegelegt --> evtl noch ändern
def validate_password(password):
    # Überprüft, ob das Passwort den Anforderungen entspricht (z.B. Länge)
    return len(password) >= 8

@password_reset_blueprint.route('/change_password', methods=['POST'])
def change_password():
    if request.method == "POST":
        # user_id würde davon ausgehen, dass der nutzer in der maske seine email / namen eingibt
        # system sollte automatisch id des nutzers durch session verwenden
        user_id = request.form["user_id"]
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        # Prüfen, ob alle Felder ausgefüllt sind
        if not current_password or not new_password or not confirm_password:
            return render_template("change_password.html", error="Bitte füllen Sie alle Felder aus.")

        # Prüfen, ob die neuen Passwörter übereinstimmen
        if new_password != confirm_password:
            return render_template("change_password.html", error="Die neuen Passwörter stimmen nicht überein.")

        # Prüfen, ob das neue Passwort den Anforderungen entspricht
        if not validate_password(new_password):
            return render_template("change_password.html", error="Das neue Passwort ist zu kurz.")

        user = get_user_by_id(user_id)
        if user:
            hashed_current_password = hash_password(current_password)

            # Überprüfen, ob das aktuelle Passwort korrekt ist
            if hashed_current_password != user.password:
                return render_template("change_password.html", error="Das aktuelle Passwort ist nicht korrekt.")

            # Aktualisieren des Passworts
            hashed_new_password = hash_password(new_password)
            update_password_for_user(user_id, hashed_new_password)

            return render_template("change_password.html", success="Das Passwort wurde erfolgreich geändert.")
        else:
            return render_template("change_password.html", error="Benutzer nicht gefunden.")

    return render_template("change_password.html")
