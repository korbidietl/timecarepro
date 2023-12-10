from flask import render_template, request, Blueprint, session
from db_query import validate_login, set_password

password_change_blueprint = Blueprint("password_change", __name__)


# ich habe jetzt mal eine minimale passwort länge von 8 festegelegt --> evtl noch ändern
def validate_password(password):
    # Überprüft, ob das Passwort den Anforderungen entspricht (z.B. Länge)
    return len(password) >= 8


@password_change_blueprint.route('/password_change', methods=['POST','GET'])
def change_password():
    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        # Prüfen, ob alle Felder ausgefüllt sind
        if not current_password or not new_password or not confirm_password:
            return render_template("password_change.html", error="Bitte füllen Sie alle Felder aus.")

        # Prüfen, ob die neuen Passwörter übereinstimmen
        elif new_password != confirm_password:
            return render_template("password_change.html", error="Die neuen Passwörter stimmen nicht überein.")

        # Prüfen, ob das neue Passwort den Anforderungen entspricht
        elif not validate_password(new_password):
            return render_template("password_change.html", error="Das neue Passwort ist zu kurz.")

        # Überprüfen, ob das aktuelle Passwort korrekt ist
        elif not validate_login(session['user_email'], current_password):
            return render_template("password_change.html", error="Das aktuelle Passwort ist nicht korrekt.")

        # Aktualisieren des Passworts
        else:
            set_password(session['user_email'], new_password)

        return render_template("password_change.html", success="Das Passwort wurde erfolgreich geändert.")

    return render_template("/password_change.html")
