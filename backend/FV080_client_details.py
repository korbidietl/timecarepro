from flask import Blueprint, render_template
from db_query import get_klient_data

client_details_blueprint = Blueprint('client_details', __name__)


@client_details_blueprint.route('/client_details/<int:client_id>', methods=['POST','GET'])
def client_details(client_id):
    client_data = get_klient_data(client_id)
    print(client_data)

    return render_template('FV080_client_details.html',client_id=client_id,
                           firstname=client_data[1],
                           lastname=client_data[2],
                           birthday=client_data[3],
                           phone=client_data[4],
                           sb=client_data[5],
                           address=client_data[6],
                           fk=client_data[7],
                           hk=client_data[8],
                           fv=client_data[9])
