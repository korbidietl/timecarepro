from flask import Blueprint, render_template, session

home_blueprint = Blueprint('home', __name__)


@home_blueprint.route('/home', methods=['POST', 'GET'])
def home():
    user_id = session.get('user_id')

    role = session.get('user_role')


    return render_template('FAN010_home.html', user_id=user_id, role=role)
