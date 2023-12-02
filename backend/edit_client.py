from flask import Flask, request, jsonify
from db_query import edit_klient

app = Flask(__name__)


@app.route('/edit_client', methods=['POST'])
def edit_client():
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


if __name__ == '__main__':
    app.run()
