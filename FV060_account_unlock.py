from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from db_query import edit_account_unlock

account_unlock_blueprint = Blueprint('account_unlock', __name__)


@account_unlock_blueprint.route('/account_unlock/<int:person_id>', methods=['POST', 'GET'])
def account_unlock(person_id):
    return_url = session.get('url')
    if request.method == 'POST':

        edit_account_unlock(person_id)
        flash("Account wurde erfolgreich entsperrt")
        return redirect(url_for('home.home'))
    return render_template('FV060_account_unlock.html', person_id=person_id, return_url=return_url)
