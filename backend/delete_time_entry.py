from flask import Blueprint, request
from db_query import delete_zeiteintrag

delete_time_entry_blueprint = Blueprint("delete te", __name__)



@delete_time_entry_blueprint.route('/delete_te')
def delete_te():
    # übergebene ID und vermerk von welcher Funktion hierher geleitet
    zeiteintrags_ID = request.form.get('zeiteintrags_ID')
    origin_function = request.form.get('origin_function')
    # Zeiteintrag wurde schon gebucht
    if :
        error= "“Die Stundennachweise für diesen Monat wurden bereits gebucht. Der Eintrag kann nicht mehr gelöscht werden."
    else:
        # Löschen der Zeiteinträge und dazugehörigen Fahrten
        delete_zeiteintrag(zeiteintrags_ID)

        # Rückleitungen zur Herkunftsfunktion
        if origin_function == 'function1':
            return redirect(url_for('name_function_1'))
        elif origin_function == 'function 2':
            return redirect(url_for('name_function_2'))
