from flask import Flask, render_template, request, jsonify
from db_query import mitarbeiter_dropdown, create_klient

app = Flask(__name__)


@app.route('/create_client', methods=['POST'])
def register_client():
    nachname = request.form.get('lastname')
    vorname = request.form.get('firstname')
    geburtsdatum = request.form.get('birthday')
    telefonnummer = request.form.get('number')
    sachbearbeiter_id = request.form.get('sbDropdown')
    adresse = request.form.get('address')
    kontingent_fk = request.form.get('fkcontingent')
    kontingent_hk = request.form.get('hkcontingent')
    fallverantwortung_id = request.form.get('fvDropdown')

    try:
        create_klient(nachname, vorname, geburtsdatum, telefonnummer, sachbearbeiter_id, adresse,
                      kontingent_hk, kontingent_fk, fallverantwortung_id)
        return jsonify({'message': 'Client successfully updated'}), 200
    except Exception as e:
        return jsonify({'message': 'Error updating client: ' + str(e)}), 500


    return render_template('create_client.html', items=mitarbeiter_dropdown())


if __name__ == '__main__':
    app.run(debug=True)

