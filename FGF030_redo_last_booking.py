from flask import flash, redirect, url_for, Blueprint, session, request, render_template
from db_query import get_last_buchung, delete_buchung


redo_booking_blueprint = Blueprint('redo_booking_blueprint', __name__, template_folder='templates')


@redo_booking_blueprint.route('/redo_last_booking/<int:client_id>', methods=['POST'])
def revidieren_buchung(client_id):
    return_url = session.get('url')
    last_buchung = get_last_buchung(client_id)
    if request.method == 'POST':
        if last_buchung:
            last_buchung_id = int(last_buchung[1])
            last_buchung_month = last_buchung[0]
            delete_buchung(last_buchung_id)
            flash(f"Buchung für Monat {last_buchung_month} wurde erfolgreich revidiert.", 'success')
            return redirect(session.pop('url', None))
        else:
            flash("Keine Buchung gefunden, die revidiert werden könnte.", 'error')
            return redirect(session.pop('url', None))

    return render_template('FGF030_redo_last_booking.html', last_buchung=last_buchung, client_id=client_id,
                           return_url=return_url)

