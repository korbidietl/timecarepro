from flask import Blueprint, render_template, request, session, redirect, url_for
from db_query import edit_account_lock, edit_account_unlock

account_management_blueprint = Blueprint("account_management", __name__)


@account_management_blueprint.route('/account_management', methods=['GET', 'POST'])
def account_management():
    # accounts = get_all_accounts()

    if request.method == 'POST':
        if 'lock_account' in request.form:
            account_id = request.form['lock_account']
            edit_account_lock(account_id)

        elif 'unlock_account' in request.form:
            account_id = request.form['unlock_account']
            edit_account_unlock(account_id)

        # Nach dem Bearbeiten der Accounts die Seite neu laden
        return redirect(url_for('.account_management'))

    return render_template('FV010_account_management.html')
