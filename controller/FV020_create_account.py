import hashlib
from controller.FNAN020_password_reset import generate_random_password, send_email
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from model.person import validate_email, create_account_db
from datetime import datetime

create_account_blueprint = Blueprint('create_account', __name__)


def is_valid_date(date_string):
    try:
        date_object = datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_phone(phone_number):
    if len(phone_number) == 10 and phone_number.isdigit():
        return True
    else:
        return False


def sha1_hash_password(password):
    # Erzeugen eines SHA-1 Hashes des Passworts
    sha1_hash = hashlib.sha1(password.encode()).hexdigest()
    return sha1_hash


def send_email_create_account(email, firstname, lastname, new_password):
    subject = "Ihr neuer Account"
    body = (f"Sehr geehrte/r {firstname} {lastname}, \n\n"
            f"Ihr automatisch generierte Passwort ist: {new_password} \n"
            f"Um Ihren Account nutzen zu können, loggen Sie sich bitte mit diesem Passwort auf der Webseite ein und "
            f"ändern diese unmittelbar..\n\n"
            f"Mit freundlichen Grüßen\n"
            f"Ihr TimeCare Pro-Team")
    send_email(email, subject, body)


@create_account_blueprint.route('/create_account', methods=['POST', 'GET'])
def create_account():
    if 'user_id' in session:
        user_role = session['user_role']
        if user_role != 'Verwaltung' and user_role != 'Geschäftsführung':
            flash('Sie sind nicht berechtigt diese Seite aufzurufen.')
            return redirect(session['secure_url'])
        else:
            # Rückleitung bei unerlaubter Seite
            session['secure_url'] = url_for('create_account.create_account')

            if request.method == 'POST':
                selected_role = request.form.get('role')
                lastname = request.form.get('lastname')
                firstname = request.form.get('firstname')
                email = request.form.get('email')
                birthday = request.form.get('birthday')
                address = request.form.get('address')
                qualification = request.form.get('qualification')
                phone = request.form.get('phone')

                # Überprüfung ob alle notwendigen Felder ausgefüllt wurden
                required_fields = ['lastname', 'firstname', 'role', 'email']

                for field in required_fields:
                    if not request.form.get(field):
                        flash('Es müssen alle Felder ausgefüllt werden.')
                        return render_template('FV020_create_account.html')
                # Überprüfen ob Email Umlaute enthält
                umlaute = {'ä', 'ö', 'ü', 'ß'}
                if any(umlaut in email for umlaut in umlaute):
                    flash('In der E-Mail Adresse dürfen keine Umlaute sein', 'error')
                    return render_template('FV020_create_account.html')

                # Überprüfung ob alle zusätzlich notwendigen Felder für Mitarbeiter ausgefüllt wurden
                if selected_role == 'Mitarbeiter':
                    additional_fields = ['birthday', 'address', 'phone']
                    for field in additional_fields:
                        value = request.form.get(field)
                        if not value:
                            flash('Bei der Rolle Mitarbeiter müssen alle benötigten Felder ausgefüllt werden.')
                            return render_template('FV020_create_account.html')

                            # Überprüfen des Datentyps
                        if field == 'birthday' and not is_valid_date(value):
                            flash(f'Eingabe in Feld {field} ungültig. Bitte geben Sie ein gültiges Datum ein.')
                            return render_template('FV020_create_account.html')
                        elif field == 'phone' and not is_valid_phone(value):
                            flash(f'Eingabe in Feld {field} ungültig. Bitte geben Sie eine gültige Telefonnummer ein.')
                            return render_template('FV020_create_account.html')
                else:
                    jahr = 1900
                    monat = 1
                    tag = 1
                    birthday = datetime(jahr, monat, tag)

                # Überprüfung ob schon ein Account existiert
                if validate_email(email):
                    flash('Es existiert bereits ein Account mit dieser E-Mail-Adresse.')
                    return render_template('FV020_create_account.html')

                else:
                    password = generate_random_password(10)
                    hashed_password = sha1_hash_password(password)
                    change_password = 1
                    create_account_db(firstname, lastname, birthday, qualification, address, selected_role, email,
                                      phone, hashed_password, 0, change_password)
                    send_email_create_account(email, firstname, lastname, password)
                    flash("Account wurde erfolgreich angelegt", "success")
                    return redirect(url_for('account_management.account_management'))

            return render_template('FV020_create_account.html')
    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))
