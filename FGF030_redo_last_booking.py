from flask import flash, redirect, Blueprint, session, request, render_template

from FV120_book_time_entries import month_number_to_name
from db_query import get_last_buchung, delete_buchung

redo_booking_blueprint = Blueprint('redo_booking_blueprint', __name__, template_folder='templates')


@redo_booking_blueprint.route('/redo_last_booking/<int:client_id>', methods=['POST', 'GET'])
def revidieren_buchung(client_id):
    return_url = session.get('url')
    last_buchung = get_last_buchung(client_id)

    if last_buchung:
        last_buchung_id = int(last_buchung[1])
        last_buchung_month = last_buchung[0]

        year, month = last_buchung_month.split('-')
        month_int = int(month)
        print(last_buchung_month)

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
