from flask import Blueprint, request, render_template, flash
from db_query import edit_account_lock, check_account_locked, edit_account_unlock

account_lock_blueprint = Blueprint('account_lock', __name__)


@account_lock_blueprint.route('/account_lock/<int:person_id>', methods=['POST', 'GET'])
def account_lock(person_id):
    if request.method == 'POST':
        edit_account_lock(person_id)
        flash("Account wurde erfolgreich gesperrt")
        return render_template('FAN010_home.html', person_id=person_id)

    return render_template('FV050_account_lock.html', person_id=person_id)
