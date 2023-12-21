from flask import Blueprint, render_template, session
from FNAN010_login import logged_in_users


logout_blueprint = Blueprint("logout", __name__)


@logout_blueprint.route('/logout')
def logout():
    email = session.get('user_email')

    # Überprüfen, ob der Benutzer eingeloggt ist
    if 'user_id' in session:
        # Benutzer aus Liste eingeloggter Benutzer entfernen
        logged_in_users.remove(email)

        # Session löschen
        session.pop('user_id', None)
        session.pop('user_role', None)
        session.pop('user_email', None)

        return render_template('FNAN010_login.html')

    else:
        # Benutzer ist nicht eingeloggt
        return render_template('FNAN010_login.html')
