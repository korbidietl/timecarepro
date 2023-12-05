from password_reset import generate_random_password, send_email
from flask import Flask, render_template, request
from db_query import validate_email, create_account, set_password_required_true
from passlib.hash import sha1_crypt
from datetime import datetime

app = Flask(__name__)


def is_valid_date(date_string):
    try:
        date_object = datetime.strptime(date_string, "%d.%m.%Y")
        return True
    except ValueError:
        return False


def is_valid_phone(phone_number):
    if len(phone_number) == 10 and phone_number.isdigit():
        return True
    else:
        return False


def send_email_create_account(email, lastname, new_password):
    subject = "Ihr neuer Account"
    body = (f"Sehr geehrte/r Frau/Mann {lastname}, \n\n"
            f"Ihr automatisch generierte Passwort ist: {new_password} \n"
            f"Um Ihren Account nutzen zu können, loggen Sie sich bitte mit diesem Passwort auf der Webseite ein und "
            f"ändern diese unmittelbar..\n\n"
            f"Mit freundlichen Grüßen\n"
            f"Ihr TimeCare Pro-Team")
    send_email(email, subject, body)


@app.route('/create_account', methods=['POST'])
def create_account():
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
            error_message = 'Es müssen alle Felder ausgefüllt werden.'
            return render_template('create_account.html', error_message=error_message)

    # Überprüfung ob alle zusätzlich notwendigen Felder für Mitarbeiter ausgefüllt wurden
    if selected_role == 'Mitarbeiter':
        additional_fields = ['birthday', 'address', 'phone']
        for field in additional_fields:
            value = request.form.get(field)
            if not value:
                error_message = 'Bei der Rolle Mitarbeiter müssen alle benötigten Felder ausgefüllt werden.'
                return render_template('create_account.html', error_message=error_message)

                # Überprüfen des Datentyps
            if field == 'birthday' and not is_valid_date(value):
                error_message = f'Eingabe in Feld {field} ungültig. Bitte geben Sie ein gültiges Datum ein.'
                return render_template('create_account.html', error_message=error_message)
            elif field == 'phone' and not is_valid_phone(value):
                error_message = f'Eingabe in Feld {field} ungültig. Bitte geben Sie eine gültige Telefonnummer ein.'
                return render_template('create_account.html', error_message=error_message)

    # Überprüfung ob schon ein Account existiert
    if validate_email(email):
        error_message = 'Es existiert bereits ein Account mit dieser E-Mail-Adresse.'
        return render_template('create_account.html', error_message=error_message)

    else:
        password = generate_random_password(10)
        hashed_password = sha1_crypt.encrypt(password)
        change_password = set_password_required_true(email)
        create_account(firstname, lastname, birthday, qualification, address, selected_role, email, phone, hashed_password, 0,
                       change_password)
        send_email_create_account(email, lastname, password)
        return render_template('account_overview.html', email=email,
                               success_message="Account wurde erfolgreich angelegt")
