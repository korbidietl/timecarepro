from flask import Blueprint, request, render_template, redirect, url_for, flash
from db_query import edit_account, get_person_data
from FV020_create_account import is_valid_phone, is_valid_date

edit_account_blueprint = Blueprint('edit_account', __name__)


@edit_account_blueprint.route('/edit_account/<int:person_id>', methods=['GET', 'POST'])
def edit_account_details(person_id):
    if request.method == 'POST':
        # Daten aus dem Formular
        lastname = request.form.get('lastname')
        firstname = request.form.get('firstname')
        birthday = request.form.get('birthday')
        address = request.form.get('address')
        phone = request.form.get('phone')
        qualification = request.form.get('qualification')
        # rolle und email sind nicht bearbeitbar

        # Überprüfen, ob alle erforderlichen Felder ausgefüllt wurden
        required_fields = ['lastname', 'firstname', 'birthday', 'address', 'phone']
        for field in required_fields:
            if not request.form.get(field):
                flash('Es müssen alle Felder ausgefüllt werden.')
                return render_template('FV040_edit_account.html', person_id=person_id)

        # Überprüfen des Datentyps für Geburtstag und Telefonnummer
        if not is_valid_date(birthday):
            flash('Das Geburtsdatum ist ungültig.')
            return render_template('FV040_edit_account.html', person_id=person_id)
        if not is_valid_phone(phone):
            flash('Die Telefonnummer ist ungültig.')
            return render_template('FV040_edit_account.html', person_id=person_id)

        # Account-Daten aktualisieren
        edit_account(person_id, firstname, lastname, birthday, qualification, address, phone)

        # Rückleitung zur vorherigen Seite
        # weiß noch nicht wie das implementiert werden soll
        # vllt so:
        if request.method == 'GET':
            return_url = request.args.get('return_url', '/default_return_page')
            return render_template('FV040_edit_account.html', person_id=person_id, return_url=return_url)

    person = get_person_data(person_id)
    return render_template('FV040_edit_account.html', person=person)


