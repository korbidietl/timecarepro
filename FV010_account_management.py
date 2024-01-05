from flask import Blueprint, render_template, request, session, redirect, url_for
from db_query import edit_account_lock, edit_account_unlock, get_steuerbuero_table, get_sachbearbeiter_table

account_management_blueprint = Blueprint("account_management", __name__)


@account_management_blueprint.route('/account_management', methods=['GET', 'POST'])
def account_management():
    # session speichern für rückleitung
    session['url'] = url_for('account_management.account_management')

    # accounts = get_all_accounts()
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
                           sachbearbeiter=sachbearbeiter)