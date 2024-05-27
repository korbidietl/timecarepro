from flask import flash, redirect, Blueprint, session, request, render_template, url_for
from controller.FV120_book_time_entries import month_number_to_name
from model.buchung import get_last_buchung, delete_buchung

redo_booking_blueprint = Blueprint('redo_booking_blueprint', __name__, template_folder='view')


@redo_booking_blueprint.route('/redo_last_booking/<int:client_id>', methods=['POST', 'GET'])
def revidieren_buchung(client_id):
    if 'user_id' in session:
        user_role = session['user_role']
        if user_role != 'Geschäftsführung':
            flash('Sie sind nicht berechtigt diese Seite aufzurufen.')
            return redirect(session['secure_url'])
        else:
            return_url = session.get('url')
            last_buchung = get_last_buchung(client_id)

            if last_buchung:
                last_buchung_id = int(last_buchung[1])
                last_buchung_month = last_buchung[0]

                year, month = last_buchung_month.split('-')
                month_int = int(month)

                month_str = month_number_to_name(month_int)

                if request.method == 'POST':
                    delete_buchung(last_buchung_id)
                    flash(f"Buchung für Monat {month_str} wurde erfolgreich revidiert.", 'success')
                    return redirect(return_url)

                return render_template('FGF030_redo_last_booking.html', last_buchung=last_buchung, client_id=client_id,
                                       return_url=return_url, month_str=month_str)
            else:
                flash("Keine Buchung gefunden, die revidiert werden könnte.", 'error')
                return redirect(return_url)

    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))
