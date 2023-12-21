from flask import Blueprint, request, render_template, flash
from db_query import edit_account_lock

account_lock_blueprint = Blueprint('account_lock', __name__)


@account_lock_blueprint.route('/account_lock/<int:person_id>', methods=['POST', 'GET'])
def account_lock(person_id):
    if request.method == 'POST':

        required_fields = ['person_id']

        for field in required_fields:
            if not request.form.get(field):
                flash('Es müssen alle Felder ausgefüllt werden.')
                return render_template('FV050_account_lock.html', person_id=person_id)

        edit_account_lock(person_id)
        return render_template('FAN010_home.html',
                               success_message="Account wurde erfolgreich gesperrt", person_id=person_id)
    return render_template('FV050_account_lock.html', person_id=person_id)
