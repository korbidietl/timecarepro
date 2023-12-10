from flask import Blueprint, render_template, request

client_hours_blueprint = Blueprint('client_hours_blueprint', __name__, template_folder='templates')

@client_hours_blueprint.route('/client/<int:client_id>')
def client_profile(client_id):
    client_id = request.form.get('client_id')
    client_name = get_client_name(client_id)
    client_sachbearbeiter = get_sachbearbeiter_name(client_id)

    return render_template('client_profile.html', client_id=client_id)
Reg
