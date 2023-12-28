from flask import Blueprint, request, render_template, redirect, url_for, flash
from db_query import edit_account, get_person_data
from FV020_create_account import is_valid_phone, is_valid_date

edit_account_blueprint = Blueprint('edit_account', __name__)


@edit_account_blueprint.route('/edit_account/<int:person_id>', methods=['GET', 'POST'])
def edit_account(person_id):
    person_data_list = get_person_data(person_id)
    person_data = person_data_list[0]

    if person_data:
        firstname = person_data[1]
        lastname = person_data[2]
        birthday = person_data[3]
        qualification = person_data[4]
        address = person_data[5]
        role = person_data[6]
        email = person_data[7]
        phone = person_data[8]
        locked = person_data[9]

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
                return render_template('FV040_edit_account.html', person_id=person_id, firstname=firstname,
                               lastname=lastname, birthday=birthday, qualification=qualification, address=address,
                               email=email, phone=phone, locked=locked, role=role)

        # Überprüfen des Datentyps für Geburtstag und Telefonnummer
        if not is_valid_date(birthday):
            flash('Das Geburtsdatum ist ungültig.')
            return render_template('FV040_edit_account.html', person_id=person_id, firstname=firstname,
                               lastname=lastname, birthday=birthday, qualification=qualification, address=address,
                               email=email, phone=phone, locked=locked, role=role)
        if not is_valid_phone(phone):
            flash('Die Telefonnummer ist ungültig.')
            return render_template('FV040_edit_account.html', person_id=person_id, firstname=firstname,
                               lastname=lastname, birthday=birthday, qualification=qualification, address=address,
                               email=email, phone=phone, locked=locked, role=role)

        # Account-Daten aktualisieren
        edit_account(person_id, firstname, lastname, birthday, qualification, address, phone)

        # Rückleitung zur vorherigen Seite
        # weiß noch nicht wie das implementiert werden soll
        # vllt so:
        if request.method == 'GET':
            return_url = request.args.get('return_url', '/default_return_page')
            return render_template('FV040_edit_account.html', person_id=person_id, firstname=firstname,
                               lastname=lastname, birthday=birthday, qualification=qualification, address=address,
                               email=email, phone=phone, locked=locked, role=role, return_url=return_url)

    return render_template('FV040_edit_account.html', person_id=person_id, firstname=firstname,
                               lastname=lastname, birthday=birthday, qualification=qualification, address=address,
                               email=email, phone=phone, locked=locked, role=role)


