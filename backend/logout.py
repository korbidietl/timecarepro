from flask import Blueprint, render_template, session
from backend.login import logged_in_users


logout_blueprint = Blueprint("logout", __name__)


@logout_blueprint.route('/logout')
def logout():
    # wie greife ich auf die richtige user_id zu
    # Überprüfen, ob der Benutzer eingeloggt ist
    if 'user_id' in session:
        # Benutzer aus Liste eingeloggter Benutzer entfernen
        logged_in_users.remove(session['user_id'])

        # Session löschen
        session.pop('user_id', None)
        session.pop('user_role', None)

        return render_template('login.html')

    else:
        # Benutzer ist nicht eingeloggt
        return render_template('login.html')
