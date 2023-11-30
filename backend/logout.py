from flask import Blueprint, render_template, redirect, url_for, session
from einloggen import logged_in_users

logout_blueprint = Blueprint("logout", __name__)


@logout_blueprint.route('/logout')
def logout():
    # Überprüfen, ob der Benutzer eingeloggt ist
    if 'user_id' in session:
        # Benutzer aus Liste eingeloggter Benutzer entfernen
        logged_in_users.remove(session['user_id'])

        # Session löschen
        session.pop('user_id', None)
        session.pop('user_role', None)

        return render_template('Einloggen.html')

    else:
        # Benutzer ist nicht eingeloggt
        return render_template('Einloggen.html')