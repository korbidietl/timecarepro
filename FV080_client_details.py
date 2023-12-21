from flask import Blueprint, render_template, url_for
from db_query import get_klient_data, get_name_by_id

client_details_blueprint = Blueprint('client_details', __name__)


@client_details_blueprint.route('/client_details/<int:client_id>', methods=['POST', 'GET'])
def client_details(client_id):
    return_url = url_for('account_management.account_management')
    # Datenbankaufruf über client_id
    client_data_list = get_klient_data(client_id)
    client_data = client_data_list[0]

    if client_data:
        firstname = client_data[1],
        lastname = client_data[2],
        birthday = client_data[3],
        phone = client_data[4],
        sb = client_data[5],
        address = client_data[6],
        fk = client_data[7],
        hk = client_data[8],
        fv = client_data[9]

        sb_id = sb[0]
        fv_id = fv

        sachbearbeiter_data = get_name_by_id(sb_id)
        sachbearbeiter = sachbearbeiter_data[0]
        fallverantwortung_data = get_name_by_id(fv_id)
        fallverantwortung = fallverantwortung_data[0]

        return render_template('FV080_client_details.html', client_id=client_id, firstname=firstname,
                               lastname=lastname, birthday=birthday, phone=phone, sb=sachbearbeiter, address=address, fk=fk, hk=hk,
                               fv=fallverantwortung, return_url=return_url)

    return render_template('FV080_client_details.html', client_id=client_id, return_url=return_url)
