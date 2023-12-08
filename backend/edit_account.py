from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime
from passlib.hash import sha1_crypt
from db_query import validate_email, create_account, edit_account, get_person_data
from email_helper import send_email
from create_account import is_valid_phone, is_valid_date

app = Flask(__name__)

@app.route('/edit_account/<int:person_id>', methods=['GET', 'POST'])
def edit_account_details(person_id):
    if request.method == 'POST':
        # Daten aus dem Formular
        lastname = request.form.get('lastname')
        firstname = request.form.get('firstname')
        birthday = request.form.get('birthday')
        address = request.form.get('address')
        phone = request.form.get('phone')
        qualification = request.form.get('qualification')

        # Überprüfen, ob alle erforderlichen Felder ausgefüllt wurden
        required_fields = ['lastname', 'firstname', 'birthday', 'address', 'phone']
        for field in required_fields:
            if not request.form.get(field):
                error_message = 'Es müssen alle Felder ausgefüllt werden.'
                return render_template('details_account.html', error_message=error_message, person_id=person_id)

        # Überprüfen des Datentyps für Geburtstag und Telefonnummer
        if not is_valid_date(birthday):
            error_message = 'Das Geburtsdatum ist ungültig.'
            return render_template('details_account.html', error_message=error_message, person_id=person_id)
        if not is_valid_phone(phone):
            error_message = 'Die Telefonnummer ist ungültig.'
            return render_template('details_account.html', error_message=error_message, person_id=person_id)

        # Account-Daten aktualisieren
        edit_account(person_id, firstname, lastname, birthday, qualification, address, phone)

        return redirect(url_for('account_overview'))

    person = get_person_data(person_id)
    return render_template('details_account.html', person=person)

# Führen Sie die Flask-App aus
if __name__ == '__main__':
    app.run(debug=True)

