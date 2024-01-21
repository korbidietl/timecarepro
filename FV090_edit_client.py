from flask import Blueprint, request, render_template, session, flash, redirect, url_for
from db_query import edit_klient_fct, mitarbeiter_dropdown, kostentraeger_dropdown, get_name_by_id, get_klient_data, \
    get_current_client, get_new_client, save_change_log
from FV020_create_account import is_valid_date, is_valid_phone

edit_client_blueprint = Blueprint('edit_client', __name__)


@edit_client_blueprint.route('/edit_client/<int:client_id>', methods=['POST', 'GET'])
def edit_client(client_id):
    if 'user_id' in session:
        user_role = session['user_role']
        if user_role != 'Verwaltung' and user_role != 'Geschäftsführung':
            flash('Sie sind nicht berechtigt diese Seite aufzurufen.')
            return redirect(session['secure_url'])
        else:
            # Rückleitung bei unerlaubter Seite
            session['secure_url'] = url_for('edit_client.edit_client', client_id=client_id)

            current_client = get_current_client(client_id)
            person = session.get('user_id')
            return_url = session.get('url')

            client_data_list = get_klient_data(client_id)

            client_data = client_data_list[0]
            firstname = client_data[1]
            lastname = client_data[2]
            birthday = client_data[3]
            phone = client_data[4]
            sb_id = client_data[5]
            address = client_data[6]
            fk = client_data[7]
            hk = client_data[8]
            fv_id = client_data[9]

            # Auswahl für Dropdown
            kostentraeger = kostentraeger_dropdown()
            fallverantwortung = mitarbeiter_dropdown()

            if request.method == 'POST':
                # Auslesen Daten aus Forumluar
                vorname = request.form.get('vorname')
                nachname = request.form.get('nachname')
                geburtsdatum = request.form.get('geburtsdatum')
                telefonnummer = request.form.get('telefonnummer')
                sachbearbeiter_id = request.form.get('ktDropdown')
                adresse = request.form.get('adresse')
                kontingent_hk = request.form.get('kontingent_hk')
                kontingent_fk = request.form.get('kontingent_fk')
                fallverantwortung_id = request.form.get('fvDropdown')

                required_fields = ['nachname', 'vorname', 'geburtsdatum', 'adresse']

                for field in required_fields:
                    value = request.form.get(field)
                    if not request.form.get(field):
                        flash(f'Es müssen alle Felder ausgefüllt werden.')
                        return render_template('FV090_edit_client.html', kostentraeger=kostentraeger, sb_id=sb_id,
                                               fallverantwortung=fallverantwortung, fv_id=fv_id, client_id=client_id,
                                               firstname=firstname, lastname=lastname, birthday=birthday,
                                               phone=phone, sb=sachbearbeiter_id, address=address, fk=fk, hk=hk,
                                               fv=fallverantwortung_id,
                                               return_url=return_url)
                    if field == 'geburtsdatum' and not is_valid_date(value):
                        flash(f'Eingabe in Feld {field} ungültig. Bitte geben Sie ein gültiges Datum ein.')
                        return render_template('FV090_edit_client.html', kostentraeger=kostentraeger, sb_id=sb_id,
                                               fallverantwortung=fallverantwortung, fv_id=fv_id, client_id=client_id,
                                               firstname=firstname, lastname=lastname, birthday=birthday,
                                               phone=phone, sb=sachbearbeiter_id, address=address, fk=fk, hk=hk,
                                               fv=fallverantwortung_id,
                                               return_url=return_url)
                    elif field == 'telefonnummer' and not is_valid_phone(value):
                        flash(f'Eingabe in Feld {field} ungültig. Bitte geben Sie eine gültige Telefonnummer ein.')
                        return render_template('FV090_edit_client.html', kostentraeger=kostentraeger, sb_id=sb_id,
                                               fallverantwortung=fallverantwortung, fv_id=fv_id, client_id=client_id,
                                               firstname=firstname, lastname=lastname, birthday=birthday,
                                               phone=phone, sb=sachbearbeiter_id, address=address, fk=fk, hk=hk,
                                               fv=fallverantwortung_id,
                                               return_url=return_url)

                # Klientdateils überschreiben
                edit_klient_fct(client_id, vorname, nachname, geburtsdatum, adresse, telefonnummer, sachbearbeiter_id,
                                kontingent_fk, kontingent_hk, fallverantwortung_id)

                # Änderungsprotokoll
                new_client = get_new_client(client_id)
                save_change_log(person, "Klient", current_client, new_client, client_data[0])

                # Rückleitung
                flash('Klient wurde erfolgreich bearbeitet')
                return redirect(session.pop('url', None))

            else:

                kostentraeger = [kt for kt in kostentraeger if kt['id'] != sb_id]
                sachbearbeiter_data = get_name_by_id(sb_id)
                if sachbearbeiter_data:
                    sb = sachbearbeiter_data[0]
                    sachbearbeiter = f"{sb[0]}, {sb[1]}"
                else:
                    sachbearbeiter = '-'

                fallverantwortung = [fv for fv in fallverantwortung if fv['id'] != fv_id]
                fallverantwortung_data = get_name_by_id(fv_id)
                if fallverantwortung_data:
                    fv = fallverantwortung_data[0]
                    fallverantwortung_name = f"{fv[0]}, {fv[1]}"
                else:
                    fallverantwortung_name = '-'

                return render_template('FV090_edit_client.html', kostentraeger=kostentraeger, sb_id=sb_id,
                                       fallverantwortung=fallverantwortung, fv_id=fv_id, client_id=client_id,
                                       firstname=firstname, lastname=lastname, birthday=birthday,
                                       phone=phone, sb=sachbearbeiter, address=address, fk=fk, hk=hk,
                                       fv=fallverantwortung_name,
                                       return_url=return_url)

    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))
