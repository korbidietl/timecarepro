from flask import Blueprint, request, flash, redirect, url_for, render_template
from db_query import delete_zeiteintrag, check_booked

delete_time_entry_blueprint = Blueprint("delete te", __name__)


@delete_time_entry_blueprint.route('/delete_te/<int:zeiteintrags_id>', methods=['POST', 'GET'])
def delete_te(zeiteintrags_id):
    if request.method == 'POST':
        # übergebene ID und vermerk von welcher Funktion hierher geleitet
        origin_function = request.form.get('origin_function')
        booked = check_booked(zeiteintrags_id)
        # Zeiteintrag wurde schon gebucht
        if booked:
            error = ("Die Stundennachweise für diesen Monat wurden bereits gebucht."
                     " Der Eintrag kann nicht mehr gelöscht werden.")
            flash(error, 'error')
            redirect(url_for('delete_te'))

        else:
            # Löschen der Zeiteinträge und dazugehörigen Fahrten
            delete_zeiteintrag(zeiteintrags_id)

            # Erfolgsmeldung
            success_message = "Eintrag erfolgreich gelöscht."
            flash(success_message, 'success')

            # Rückleitungen zur Herkunftsfunktion
            if origin_function == 'function1':
                return redirect(url_for('name_function_1'))
            elif origin_function == 'function 2':
                return redirect(url_for('name_function_2'))

    return render_template('/delete_time_entry.html')
