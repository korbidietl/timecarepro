from flask import Blueprint, session, redirect, url_for
from controller.FNAN010_login import logged_in_users

logout_blueprint = Blueprint("logout", __name__)


@logout_blueprint.route('/logout')
def logout():
    email = session.get('user_email')

    # Überprüfen, ob der Benutzer eingeloggt ist
    if 'user_id' in session:
        # Benutzer aus Liste eingeloggter Benutzer entfernen
        if email in logged_in_users:
            logged_in_users.remove(email)

        # Session löschen
        session.clear()

        return redirect(url_for('login.login'))

    else:
        # Benutzer ist nicht eingeloggt
        return redirect(url_for('login.login'))
