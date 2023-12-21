from flask import session, redirect, url_for, flash
from datetime import datetime, timedelta


def make_session_permanent():
    session.permanent = False


def check_session_timeout():
    session_timeout = 30  # Inaktivitätszeit in Minuten
    now = datetime.utcnow()

    last_activity = session.get('last_activity')
    if last_activity:
        last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
        if now - last_activity > timedelta(minutes=session_timeout):
            session.clear()  # Bereinigt die gesamte Session
            flash('Ihre Session ist abgelaufen. Bitte loggen Sie sich erneut ein.', 'warning')
            return redirect(url_for('login.login'))

    session['last_activity'] = now.strftime('%Y-%m-%d %H:%M:%S')
