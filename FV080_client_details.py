from flask import Blueprint, render_template, session, url_for
from db_query import get_klient_data, get_name_by_id

client_details_blueprint = Blueprint('client_details', __name__)


@client_details_blueprint.route('/client_details/<int:client_id>', methods=['POST', 'GET'])
def client_details(client_id):
    # Rückleitung bei unerlaubter Seite
    session['secure_url'] = url_for('client_details.client_details', client_id=client_id)

    return_url = session.get('url')
    client_data_list = get_klient_data(client_id)

    # Überprüfen Sie, ob client_data_list Daten enthält
    if client_data_list:
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

        sachbearbeiter = get_name_by_id(sb_id)[0] if sb_id else "N/A"
        fallverantwortung = get_name_by_id(fv_id)[0] if fv_id else "N/A"

        return render_template('FV080_client_details.html', client_id=client_id, firstname=firstname,
                               lastname=lastname, birthday=birthday, phone=phone, sb=sachbearbeiter, address=address,
                               fk=fk, hk=hk, fv=fallverantwortung, return_url=return_url)

    # Rendern der Vorlage, auch wenn keine Daten gefunden wurden
    return render_template('FV080_client_details.html', client_id=client_id, return_url=return_url)
