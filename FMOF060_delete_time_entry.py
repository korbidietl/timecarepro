from flask import Blueprint, request, flash, redirect, url_for, render_template, session
from db_query import delete_zeiteintrag, check_booked

delete_time_entry_blueprint = Blueprint("delete_te", __name__)


@delete_time_entry_blueprint.route('/delete_te/<int:zeiteintrags_id>', methods=['POST', 'GET'])
def delete_te(zeiteintrags_id):
    return_url = session.get('url')
    if request.method == 'POST':
        # übergebene ID und vermerk von welcher Funktion hierher geleitet
        booked = check_booked(zeiteintrags_id)
        # Zeiteintrag wurde schon gebucht
        if booked:
            error = ("Die Stundennachweise für diesen Monat wurden bereits gebucht."
                     " Der Eintrag kann nicht mehr gelöscht werden.")
            flash(error, 'error')
            render_template('FMOF060_delete_time_entry.html', zeiteintrags_id=zeiteintrags_id)

        else:
            # Löschen der Zeiteinträge und dazugehörigen Fahrten
            delete_zeiteintrag(zeiteintrags_id)

            # Erfolgsmeldung
            success_message = "Eintrag erfolgreich gelöscht."
            flash(success_message, 'success')

            # Rückleitungen zur Herkunftsfunktion und löschen aus der Session
            return redirect(session.pop('url', None))
    return render_template('FMOF060_delete_time_entry.html', zeiteintrags_id=zeiteintrags_id, return_url=return_url)

