from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from db_query import edit_account_lock

account_lock_blueprint = Blueprint('account_lock', __name__)


@account_lock_blueprint.route('/account_lock/<int:person_id>', methods=['POST', 'GET'])
def account_lock(person_id):
    if 'user_id' in session:
        user_role = session['user_role']
        if user_role != 'Verwaltung' and user_role != 'Geschäftsführung':
            flash('Sie sind nicht berechtigt diese Seite aufzurufen.')
            return redirect(session['secure_url'])
        else:
            return_url = session.get('url')
            if request.method == 'POST':
                edit_account_lock(person_id)
                flash("Account wurde erfolgreich gesperrt")
                return redirect(url_for('home.home'))

            return render_template('FV050_account_lock.html', person_id=person_id, return_url=return_url)

    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))
