from flask import Blueprint, request, render_template, url_for
from db_query import get_firstname_by_email, get_lastname_by_email

account_details_blueprint = Blueprint('account_details', __name__)


@account_details_blueprint.route('/account_details/<int:person_id>', methods=['POST', 'GET'])
def account_details(person_id):

    # Datenbankaufruf über person_id
    # Datenbankaufruf ob gesperrt
    # Datenbankaufruf nach role
    locked = True
    role = 'Mitarbeiter'
    user_name = 'Hallo'

    return render_template('account_details.html', person_id=person_id, locked=locked, role=role)
