from flask import session, redirect, url_for
from datetime import datetime, timedelta
from backend.login import logged_in_users


def before_request():
    # Überprüfen, ob der Benutzer eingeloggt ist und ob die letzte Aktivität länger als 30 Minuten her ist
    if 'user_id' in session and 'last_activity' in session:
        last_activity = session['last_activity']
        if datetime.utcnow() - last_activity > timedelta(minutes=30):
            # Benutzer aus Liste eingeloggter Benutzer entfernen
            logged_in_users.remove(session['user_id'])

            # Session löschen
            session.pop('user_id', None)
            session.pop('user_role', None)
            session.pop('last_activity', None)

            return redirect(url_for('einloggen.login'))

    # Aktualisiere die letzte Aktivität
    session['last_activity'] = datetime.utcnow()
