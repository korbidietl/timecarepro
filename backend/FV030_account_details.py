from flask import Blueprint, request, render_template, url_for
from db_query import get_firstname_by_email, get_lastname_by_email

account_details_blueprint = Blueprint('account_details', __name__)

account_details_blueprint.route('/account_details', methods=['POST', 'GET'])
def account_details(user_id):
    if request.method == 'POST':
        user_name =



    return render_template('FV030_account_details.py', user_id=user_id)