from flask import render_template, request, Blueprint, flash, redirect, url_for, session
from model.person import mitarbeiter_dropdown, kostentraeger_dropdown
from model.klient import create_klient, validate_client
from FV020_create_account import is_valid_date, is_valid_phone

create_client_blueprint = Blueprint("create_client", __name__)


@create_client_blueprint.route('/create_client', methods=['POST', 'GET'])
def register_client():
    if 'user_id' in session:
        user_role = session['user_role']
        if user_role != 'Verwaltung' and user_role != 'Geschäftsführung':
            flash('Sie sind nicht berechtigt diese Seite aufzurufen.')
            return redirect(session['secure_url'])
        else:
            # Rückleitung bei unerlaubter Seite
            session['secure_url'] = url_for('create_client.register_client')

            if request.method == 'POST':
                nachname = request.form.get('lastname')
                vorname = request.form.get('firstname')
                geburtsdatum = request.form.get('birthday')
                telefonnummer = request.form.get('number')
                sachbearbeiter_id = request.form.get('ktDropdown')
                adresse = request.form.get('address')
                kontingent_fk_ = request.form.get('fkontingent')
                kontingent_hk_ = request.form.get('hkontingent')
                fallverantwortung_id = request.form.get('fvDropdown')

                required_fields = ['lastname', 'firstname', 'birthday', 'address']

                for field in required_fields:
                    value = request.form.get(field)
                    if not request.form.get(field):
                        flash('Es müssen alle Felder ausgefüllt werden.')
                        return render_template('FV070_create_client.html')
                    if field == 'birthday' and not is_valid_date(value):
                        flash(f'Eingabe in Feld {field} ungültig. Bitte geben Sie ein gültiges Datum ein.')
                        return render_template('FV070_create_client.html')
                    elif field == 'phone' and not is_valid_phone(value):
                        flash(f'Eingabe in Feld {field} ungültig. Bitte geben Sie eine gültige Telefonnummer ein.')
                        return render_template('FV070_create_client.html')

                if kontingent_fk_:
                    kontingent_fk = kontingent_fk_
                else:
                    kontingent_fk = 0

                if kontingent_hk_:
                    kontingent_hk = kontingent_hk_
                else:
                    kontingent_hk = 0

                # überprüfung ob Klient existiert
                if validate_client(vorname, nachname, geburtsdatum):
                    flash('Es existiert bereits ein Client mit diesem Namen und dem Geburtsdatum.')
                    return render_template('FV070_create_client.html')

                else:
                    create_klient(vorname, nachname, geburtsdatum, telefonnummer, sachbearbeiter_id, adresse,
                                  kontingent_hk, kontingent_fk, fallverantwortung_id)
                    flash("Klient wurde erfolgreich angelegt", "success")
                    return redirect(url_for('account_management.account_management'))

            kostentraeger = kostentraeger_dropdown()
            kt = {'kostentraeger': kostentraeger}
            fallverantwortung = mitarbeiter_dropdown()
            fv = {'fallverantwortung': fallverantwortung}
            return render_template('FV070_create_client.html', **kt, **fv)

    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))
