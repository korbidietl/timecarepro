from flask import session, redirect, url_for, flash
from datetime import datetime, timedelta


def make_session_not_permanent():
    session.permanent = False


def check_session_timeout():
    # 30 Minuten inaktivität
    session_timeout = 30
    now = datetime.utcnow()

    #Automatisches Ausloggen
    last_activity = session.get('last_activity')
    if last_activity:
        last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
        if now - last_activity > timedelta(minutes=session_timeout):
            session.clear()  # Bereinigt die gesamte Session
            flash('Ihre Session ist abgelaufen. Bitte loggen Sie sich erneut ein.', 'warning')
            return redirect(url_for('login.login'))

    session['last_activity'] = now.strftime('%Y-%m-%d %H:%M:%S')
