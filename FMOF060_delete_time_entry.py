from flask import Blueprint, request, flash, redirect, url_for, render_template
from db_query import delete_zeiteintrag, check_booked

delete_time_entry_blueprint = Blueprint("delete_te", __name__)


@delete_time_entry_blueprint.route('/delete_te/<int:zeiteintrags_id>/<origin>', methods=['POST', 'GET'])
def delete_te(zeiteintrags_id, client_id, origin):
    if request.method == 'POST':
        # übergebene ID und vermerk von welcher Funktion hierher geleitet
        origin_function = request.form.get('origin_function')
        booked = check_booked(zeiteintrags_id)
        # Zeiteintrag wurde schon gebucht
        if booked:
            error = ("Die Stundennachweise für diesen Monat wurden bereits gebucht."
                     " Der Eintrag kann nicht mehr gelöscht werden.")
            flash(error, 'error')
            render_template('FMOF060_delete_time_entry.html', zeiteintrags_id=zeiteintrags_id, client_id=client_id,
                            origin=origin)

        else:
            # Löschen der Zeiteinträge und dazugehörigen Fahrten
            delete_zeiteintrag(zeiteintrags_id)

            # Erfolgsmeldung
            success_message = "Eintrag erfolgreich gelöscht."
            flash(success_message, 'success')

            # Rückleitungen zur Herkunftsfunktion
            if origin_function == 'view':
                return redirect(url_for('view_time_entries.view_time_entries', client_id=client_id))
            elif origin_function == 'show':
                return redirect(url_for('client_supervision_hours.client_supervision_hours', client_id=client_id))

    return render_template('FMOF060_delete_time_entry.html', zeiteintrags_id=zeiteintrags_id, client_id=client_id,
                           origin=origin)
