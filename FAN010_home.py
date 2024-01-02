from flask import Blueprint, render_template, session

home_blueprint = Blueprint('home', __name__)


@home_blueprint.route('/home', methods=['POST', 'GET'])
def home():
    user_id = session.get('user_id')
    print(user_id)

    return render_template('FAN010_home.html', user_id=user_id)
