from flask import Blueprint, request, render_template, redirect, flash, session
from db_query import edit_account_fct, get_person_data, get_current_person, get_new_person, save_change_log
from FV020_create_account import is_valid_phone, is_valid_date

edit_account_blueprint = Blueprint('edit_account', __name__)


@edit_account_blueprint.route('/edit_account/<int:person_id>', methods=['GET', 'POST'])
def edit_account(person_id):
    return_url = session.get('url')

    # account zustand vor änderung speichern
    current_person = get_current_person(person_id)
    person = session.get('user_id')

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
        locked = person_data[10]

    if request.method == 'POST':
        # Daten aus dem Formular
        lastname = request.form.get('lastname')
        firstname = request.form.get('firstname')
        birthday = request.form.get('birthday')
        address = request.form.get('address')
        phone = request.form.get('phone')
        qualification = request.form.get('qualification')

        # Überprüfen des Datentyps für Geburtstag und Telefonnummer
        if not is_valid_date(birthday):
            flash('Das Geburtsdatum ist ungültig.')
            return render_template('FV040_edit_account.html', person_id=person_id, firstname=firstname,
                                   lastname=lastname, birthday=birthday, qualification=qualification, address=address,
                                   email=email, phone=phone, locked=locked, role=role, return_url=return_url)

        if phone != "":
            if not is_valid_phone(phone):
                flash('Die Telefonnummer ist ungültig.')
                return render_template('FV040_edit_account.html', person_id=person_id, firstname=firstname,
                                       lastname=lastname, birthday=birthday, qualification=qualification,
                                       address=address,
                                       email=email, phone=phone, locked=locked, role=role, return_url=return_url)

        # Account-Daten aktualisieren
        edit_account_fct(firstname, lastname, birthday, qualification, address, phone, person_id)

        # änderungen in protokoll speichern
        new_person = get_new_person(person_id)
        save_change_log(person, "Account", current_person, new_person, person_data[0])

        # Rückleitung zur vorherigen Seite
        flash('Account wurde erfolgreich bearbeitet')
        return redirect(session.pop('url', None))

    return render_template('FV040_edit_account.html', person_id=person_id, firstname=firstname,
                           lastname=lastname, birthday=birthday, qualification=qualification, address=address,
                           email=email, phone=phone, locked=locked, role=role, return_url=return_url)
