from flask import Flask, render_template, request, jsonify, Blueprint, flash, redirect, url_for
from db_query import mitarbeiter_dropdown, create_klient, validate_client, kostentraeger_dropdown

# app = Flask(__name__)

create_client_blueprint = Blueprint("create_client", __name__)


@create_client_blueprint.route('/create_client', methods=['POST', 'GET'])
def register_client():
    if request.method == 'POST':
        nachname = request.form.get('lastname')
        vorname = request.form.get('firstname')
        geburtsdatum = request.form.get('birthday')
        telefonnummer = request.form.get('number')
        sachbearbeiter_id = request.form.get('ktDropdown')
        adresse = request.form.get('address')
        kontingent_fk = request.form.get('fkontingent')
        kontingent_hk = request.form.get('hkontingent')
        fallverantwortung_id = request.form.get('fvDropdown')

        required_fields = ['lastname', 'firstname', 'birthday', 'address']

        for field in required_fields:
            if not request.form.get(field):
                flash('Es müssen alle Felder ausgefüllt werden.')
                return render_template('FV070_create_client.html')

        # validate client in db_query hinzufügen (validate_email(email))
        if validate_client(vorname, nachname, geburtsdatum):
            flash('Es existiert bereits ein Client mit diesem Namen und dem Geburtsdatum.')
            return render_template('FV070_create_client.html')

        else:
            create_klient(nachname, vorname, geburtsdatum, telefonnummer, sachbearbeiter_id, adresse,
                          kontingent_hk, kontingent_fk, fallverantwortung_id)
            return redirect(url_for('account_management.account_management', success_message="Client wurde erfolgreich angelegt"))

    kostentraeger = kostentraeger_dropdown()
    kt = {'kostentraeger': kostentraeger}
    fallverantwortung = mitarbeiter_dropdown()
    fv = {'fallverantwortung': fallverantwortung}
    return render_template('FV070_create_client.html', **kt, **fv)

