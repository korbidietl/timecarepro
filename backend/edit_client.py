from flask import Blueprint, request, jsonify, render_template
from db_query import edit_klient

edit_client_blueprint = Blueprint('edit_client', __name__)


@edit_client_blueprint.route('/edit_client', methods=['POST', 'GET'])
def edit_client():
    if request.method == 'POST':
        client_id = request.form['client_id']
        vorname = request.form['vorname']
        nachname = request.form['nachname']
        geburtsdatum = request.form['geburtsdatum']
        telefonnummer = request.form['telefonnummer']
        sachbearbeiter_id = request.form['sbDropdown']
        adresse = request.form['adresse']
        kontingent_hk = request.form['kontingent_hk']
        kontingent_fk = request.form['kontingent_fk']
        fallverantwortung_id = request.form['fvDropdown']

        try:
            edit_klient(client_id, vorname, nachname, geburtsdatum, telefonnummer, sachbearbeiter_id, adresse,
                        kontingent_hk, kontingent_fk, fallverantwortung_id)
            return jsonify({'message': 'Client successfully updated'}), 200
        except Exception as e:
            return jsonify({'message': 'Error updating client: ' + str(e)}), 500

    return render_template('edit_client.html')
