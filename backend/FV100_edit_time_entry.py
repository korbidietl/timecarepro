from flask import Blueprint, Flask, render_template, request, redirect, url_for, session
from db_query import  edit_zeiteintrag # return_zeiteintrag --> get_zeiteintrag_with_fahrten_by_id?

edit_time_entry_blueprint = Blueprint('edit_time_entry', __name__)


@edit_time_entry_blueprint.route('/edit_time_entry/<int:zeiteintrag_id>', methods=['GET', 'POST'])
def edit_time_entry(zeiteintrag_id):
    if request.method == 'POST':
        # Annahme, dass die Formulardaten die erforderlichen Werte enthalten
        datum = request.form.get('datum')
        start_zeit = request.form.get('startZeit')
        end_zeit = request.form.get('endZeit')
        kilometer = request.form.get('kilometer')
        klient_id = request.form.get('klient')
        beschreibung = request.form.get('beschreibung')
        interne_notiz = request.form.get('interneNotiz')
        unterschrift_mitarbeiter = request.form.get('unterschriftMitarbeiter')
        unterschrift_klient = request.form.get('unterschriftKlient')

        # Aktualisieren des Zeiteintrags
        edit_zeiteintrag(zeiteintrag_id, start_zeit, end_zeit, unterschrift_mitarbeiter, unterschrift_klient)

        # Weiterleiten nach dem Aktualisieren
        return redirect(url_for('irgendeine_weitere_route'))

    # Wenn die Methode GET ist, lädt die Seite zum Bearbeiten
    # lädt die daten aus der datenbank und pflegt sie in das html file ein
    # zeiteintrag_data, fahrten_data = return_zeiteintrag(zeiteintrag_id)
    # return render_template('edit_time_entry.html', zeiteintrag=zeiteintrag_data, fahrten=fahrten_data)



