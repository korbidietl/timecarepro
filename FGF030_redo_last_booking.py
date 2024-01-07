from flask import flash, redirect, url_for, Blueprint, session
from db_query import get_last_buchung, delete_buchung


redo_booking_blueprint = Blueprint('redo_booking_blueprint', __name__, template_folder='templates')


@redo_booking_blueprint.route('/redo_last_booking/<int:client_id>', methods=['POST'])
def revidieren_buchung(client_id):
    last_buchung = get_last_buchung(client_id)
    if last_buchung:
        last_buchung_id = int(last_buchung['id'])
        print(last_buchung_id)
        delete_buchung(last_buchung_id)
        flash(f"Buchung für {last_buchung} wurde erfolgreich revidiert.", 'success')
    else:
        flash("Keine Buchung gefunden, die revidiert werden könnte.", 'error')
    return redirect(session.pop('url', None))

