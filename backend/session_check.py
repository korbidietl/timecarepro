from flask import session, redirect, url_for, flash
from datetime import datetime, timedelta
from backend.login import logged_in_users


def make_session_permanent():
    session.permanent = True


def check_session_timeout():
    session.modified = True
    if 'user_email' not in session:
        flash('Ihre Session ist abgelaufen. Bitte loggen Sie sich erneut ein.', 'warning')
        return redirect(url_for('login_blueprint.login'))
