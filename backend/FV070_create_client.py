from flask import Flask, render_template, request, jsonify, Blueprint
from db_query import mitarbeiter_dropdown, create_klient, validate_client

# app = Flask(__name__)

create_client_blueprint = Blueprint("create_client", __name__)


@create_client_blueprint.route('/create_client', methods=['POST', 'GET'])
def register_client():
    if request.method == 'POST':
        nachname = request.form.get('lastname')
        vorname = request.form.get('firstname')
        geburtsdatum = request.form.get('birthday')
        telefonnummer = request.form.get('number')
        sachbearbeiter_id = request.form.get('sbDropdown')
        adresse = request.form.get('address')
        kontingent_fk = request.form.get('fkcontingent')
        kontingent_hk = request.form.get('hkcontingent')
        fallverantwortung_id = request.form.get('fvDropdown')

        required_fields = ['lastname', 'firstname', 'birthday', 'address']

        for field in required_fields:
            if not request.form.get(field):
                error_message = 'Es müssen alle Felder ausgefüllt werden.'
                return render_template('create_client.html', error_message=error_message)

        # validate client in db_query hinzufügen (validate_email(email))
        if validate_client(vorname, nachname, geburtsdatum):
            error_message = 'Es existiert bereits ein Client mit diesem Namen und dem Geburtsdatum.'
            return render_template('create_client.html', error_message=error_message)

        else:
            create_klient(nachname, vorname, geburtsdatum, telefonnummer, sachbearbeiter_id, adresse,
                          kontingent_hk, kontingent_fk, fallverantwortung_id)
            return render_template('home.html',
                                   success_message="Client wurde erfolgreich angelegt")
    return render_template('create_client.html')
