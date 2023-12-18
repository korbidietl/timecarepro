from flask import Blueprint, request, render_template, session

home_blueprint = Blueprint('home', __name__)


@home_blueprint.route('/home', methods=['POST', 'GET'])
def home():

    return render_template('/FAN010_home.html')
