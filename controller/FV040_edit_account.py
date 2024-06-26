from datetime import datetime
from flask import Blueprint, request, render_template, redirect, flash, session, url_for
from model.protokoll import save_change_log
from model.person import get_current_person, get_new_person, get_person_data, edit_account_fct
from controller.FV020_create_account import is_valid_phone, is_valid_date

edit_account_blueprint = Blueprint('edit_account', __name__)


@edit_account_blueprint.route('/edit_account/<int:person_id>', methods=['GET', 'POST'])
def edit_account(person_id):
    if 'user_id' in session:
        user_role = session['user_role']
        if user_role != 'Verwaltung' and user_role != 'Geschäftsführung':
            flash('Sie sind nicht berechtigt diese Seite aufzurufen.')
            return redirect(session['secure_url'])
        else:
            # Rückleitung bei unerlaubter Seite
            session['secure_url'] = url_for('edit_account.edit_account', person_id=person_id)

            return_url = session.get('url')

            # account zustand vor änderung speichern
            current_person = get_current_person(person_id)
            person = session.get('user_id')

            # Default werte für Eingaben
            email = ""
            locked = 0
            role = ""
            firstname = ""
            lastname = ""
            jahr = 1900
            monat = 1
            tag = 1
            birthday = datetime(jahr, monat, tag)
            qualification = ""
            address = ""
            phone = ""

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
                if birthday is not None:
                    if not is_valid_date(birthday):
                        flash('Das Geburtsdatum ist ungültig.')
                        return render_template('FV040_edit_account.html', person_id=person_id, firstname=firstname,
                                               lastname=lastname, birthday=birthday, qualification=qualification,
                                               address=address, email=email, phone=phone, locked=locked, role=role,
                                               return_url=return_url)

                if phone is not None:
                    if not is_valid_phone(phone):
                        flash('Die Telefonnummer ist ungültig.')
                        return render_template('FV040_edit_account.html', person_id=person_id, firstname=firstname,
                                               lastname=lastname, birthday=birthday, qualification=qualification,
                                               address=address, email=email, phone=phone, locked=locked, role=role,
                                               return_url=return_url)

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

    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))
