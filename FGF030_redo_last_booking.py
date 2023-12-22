from flask import flash, redirect, url_for, Blueprint
from db_query import get_last_buchung, delete_buchung


redo_booking_blueprint = Blueprint('redo_booking_blueprint', __name__, template_folder='templates')


@redo_booking_blueprint.route('/redo__last_booking', methods=['POST')
def revidieren_buchung(client_id):
    last_buchung = get_last_buchung(client_id)
    if last_buchung:
        delete_buchung(last_buchung['id'])
        flash(f"Buchung für Monat {last_buchung['Monat']} wurde erfolgreich revidiert.", 'success')
    else:
        flash("Keine Buchung gefunden, die revidiert werden könnte.", 'error')
    return redirect(url_for('your_redirect_page'))