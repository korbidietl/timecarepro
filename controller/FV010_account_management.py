from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from model.person import get_steuerbuero_table, get_sachbearbeiter_table, edit_account_lock, edit_account_unlock

account_management_blueprint = Blueprint("account_management", __name__)


@account_management_blueprint.route('/account_management', methods=['GET', 'POST'])
def account_management():
    if 'user_id' in session:
        user_role = session['user_role']
        if user_role != 'Verwaltung' and user_role != 'Geschäftsführung':
            flash('Sie sind nicht berechtigt diese Seite aufzurufen.')
            return redirect(session['secure_url'])
        else:
            # Rückleitung bei unerlaubter Seite
            session['secure_url'] = url_for('account_management.account_management')

            # session speichern für rückleitung
            session['url'] = url_for('account_management.account_management')
            user_id = session.get('user_id')
            role = session.get('user_role')

            # abruf zusätzlicher Tabellen
            steuerbueros = get_steuerbuero_table()
            sachbearbeiter = get_sachbearbeiter_table()

            if request.method == 'POST':
                if 'lock_account' in request.form:
                    account_id = request.form['lock_account']
                    edit_account_lock(account_id)

                elif 'unlock_account' in request.form:
                    account_id = request.form['unlock_account']
                    edit_account_unlock(account_id)

                # Nach dem Bearbeiten der Accounts die Seite neu laden
                return redirect(url_for('.account_management'))

            return render_template('FV010_account_management.html',
                                   steuerbueros=steuerbueros,
                                   sachbearbeiter=sachbearbeiter, user_id=user_id, role=role)
    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))
