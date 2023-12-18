from flask import Blueprint, request, render_template
from db_query import edit_account_unlock

account_unlock_blueprint = Blueprint('account_unlock', __name__)


@account_unlock_blueprint.route('/account_unlock/<int:person_id>', methods=['POST', 'GET'])
def account_unlock(person_id):
    if request.method == 'POST':

        required_fields = ['person_id']

        for field in required_fields:
            if not request.form.get(field):
                error_message = 'Es müssen alle Felder ausgefüllt werden.'
                return render_template('FV060_account_unlock.html', error_message=error_message, person_id=person_id)

        edit_account_unlock(person_id)
        return render_template('FAN010_home.html',
                               success_message="Account wurde erfolgreich entsperrt", person_id=person_id)
    return render_template('FV060_account_unlock.html', person_id=person_id)
