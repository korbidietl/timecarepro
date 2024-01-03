import base64

from flask import Blueprint, render_template, session, url_for
from db_query import get_zeiteintrag_by_id, get_fahrt_by_zeiteintrag, get_klient_data

work_hours_details_blueprint = Blueprint('work_hours_details', __name__)


@work_hours_details_blueprint.route('/work_hours_details/<int:zeiteintrag_id>/<int:person_id>')
def show_details(zeiteintrag_id, person_id):
    session['url'] = url_for('work_hours_details.show_details', zeiteintrag_id=zeiteintrag_id, person_id=person_id)
    # Datenbankaufrufe
    zeiteintrag_liste = get_zeiteintrag_by_id(zeiteintrag_id)
    zeiteintrag = zeiteintrag_liste[0]
    datum = zeiteintrag[3].strftime("%Y-%m-%d")
    von = zeiteintrag[3].strftime("%H:%M")
    bis = zeiteintrag[4].strftime("%H:%M")

    fahrten = get_fahrt_by_zeiteintrag(zeiteintrag_id)

    # Name Klient
    klient_id = zeiteintrag[6]
    klient_data = get_klient_data(klient_id)
    klient_name = klient_data[0][1] +' '+ klient_data[0][2]



    # Umwandlung Unterschriften
    if zeiteintrag[1]:
        unterschrift_mitarbeiter = base64.b64encode(zeiteintrag[1]).decode('utf-8')
    else:
        unterschrift_mitarbeiter = ""

    if zeiteintrag[2]:
        unterschrift_klient = base64.b64encode(zeiteintrag[2]).decode('utf-8')
    else:
        unterschrift_klient = ""

    return render_template('FMOF040_work_hours_details.html', zeiteintrag=zeiteintrag, fahrten=fahrten,
                           klient_name=klient_name, datum=datum, von=von, bis=bis,
                           unterschrift_klient=unterschrift_klient,
                           unterschrift_mitarbeiter=unterschrift_mitarbeiter, zeiteintrag_id=zeiteintrag_id,
                           person_id=person_id)
