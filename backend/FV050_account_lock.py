from flask import Blueprint, request, render_template
from db_query import edit_account_lock

account_lock_blueprint = Blueprint('account_lock', __name__)


@account_lock_blueprint.route('/account_lock', methods=['POST', 'GET'])
def account_lock():
    if request.method == 'POST':
        person_id = request.form.get('person_id')

        required_fields = ['person_id']

        for field in required_fields:
            if not request.form.get(field):
                error_message = 'Es müssen alle Felder ausgefüllt werden.'
                return render_template('FV050_account_lock.html', error_message=error_message)

        edit_account_lock(person_id)
        return render_template('FAN010_home.html',
                               success_message="Account wurde erfolgreich gesperrt")
    return render_template('FV050_account_lock.html')
