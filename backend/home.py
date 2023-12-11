from flask import Blueprint, request, render_template

home_blueprint = Blueprint('home', __name__)


@home_blueprint.route('/home', methods=['POST', 'GET'])
def home():
    if request.method('POST'):
        return render_template('/home.html')

    return render_template('/home.html')
