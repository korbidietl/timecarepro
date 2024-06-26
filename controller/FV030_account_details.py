from flask import Blueprint, render_template, url_for, session, flash, redirect
from model.person import get_person_data

account_details_blueprint = Blueprint('account_details', __name__)


@account_details_blueprint.route('/account_details/<int:person_id>', methods=['POST', 'GET'])
def account_details(person_id):
    if 'user_id' in session:
        user_role = session['user_role']
        if user_role != 'Verwaltung' and user_role != 'Geschäftsführung':
            flash('Sie sind nicht berechtigt diese Seite aufzurufen.')
            return redirect(session['secure_url'])
        else:
            # Rückleitung bei unerlaubter Seite
            session['secure_url'] = url_for('account_details.account_details', person_id=person_id)

            return_url = session.get('url')
            # session speichern für rückleitung
            session['url'] = url_for('account_details.account_details', person_id=person_id)

            # Datenbankaufruf über person_id
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

                return render_template('FV030_account_details.html', person_id=person_id, firstname=firstname,
                                       lastname=lastname, birthday=birthday, qualification=qualification,
                                       address=address, email=email, phone=phone, locked=locked, role=role,
                                       return_url=return_url)

            return render_template('FV030_account_details.html', person_id=person_id, return_url=return_url)

    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))
