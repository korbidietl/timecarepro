from flask import Blueprint, request, render_template, flash
from db_query import edit_account_unlock

account_unlock_blueprint = Blueprint('account_unlock', __name__)


@account_unlock_blueprint.route('/account_unlock/<int:person_id>', methods=['POST', 'GET'])
def account_unlock(person_id):
    if request.method == 'POST':

        edit_account_unlock(person_id)
        flash("Account wurde erfolgreich entsperrt")
        return render_template('FAN010_home.html', person_id=person_id)
    return render_template('FV060_account_unlock.html', person_id=person_id)
