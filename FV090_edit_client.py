from flask import Blueprint, request, jsonify, render_template, session
from db_query import edit_klient, mitarbeiter_dropdown, kostentraeger_dropdown, get_name_by_id, get_klient_data, get_current_client, get_new_client, save_change_log

edit_client_blueprint = Blueprint('edit_client', __name__)

@edit_client_blueprint.route('/edit_client/<int:client_id>', methods=['POST', 'GET'])
def edit_client(client_id):
    current_client = get_current_client(client_id)
    person = session.get('user_id')

    client_data_list = get_klient_data(client_id)

    kostentraeger = kostentraeger_dropdown()
    fallverantwortung = mitarbeiter_dropdown()

    if client_data_list and request.method == 'POST':
        client_data = client_data_list[0]
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

            new_client = get_new_client(client_id)
            save_change_log(person, "Klient", current_client, new_client)
            return jsonify({'message': 'Client successfully updated'}), 200
        except Exception as e:
            return jsonify({'message': 'Error updating client: ' + str(e)}), 500

    elif client_data_list:
        client_data = client_data_list[0]
        firstname = client_data[1]
        lastname = client_data[2]
        birthday = client_data[3]
        phone = client_data[4]
        sb_id = client_data[5]
        address = client_data[6]
        fk = client_data[7]
        hk = client_data[8]
        fv_id = client_data[9]

        sachbearbeiter_data = get_name_by_id(sb_id)
        sachbearbeiter = sachbearbeiter_data[0] if sachbearbeiter_data else '-'
        fallverantwortung_data = get_name_by_id(fv_id)
        fallverantwortung_name = fallverantwortung_data[0] if fallverantwortung_data else '-'

        return render_template('FV090_edit_client.html', kostentraeger=kostentraeger, fallverantwortung=fallverantwortung,
                               client_id=client_id, firstname=firstname, lastname=lastname, birthday=birthday,
                               phone=phone, sb=sachbearbeiter, address=address, fk=fk, hk=hk, fv=fallverantwortung_name)

    return render_template('FV090_edit_client.html', kostentraeger=kostentraeger, fallverantwortung=fallverantwortung, client_id=client_id)


