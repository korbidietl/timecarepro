import base64
from flask import Blueprint, render_template, session, url_for, flash, redirect
from model.klient import get_klient_data
from model.fahrt import get_fahrt_by_zeiteintrag
from model.zeiteintrag import get_zeiteintrag_by_id, check_booked

work_hours_details_blueprint = Blueprint('work_hours_details', __name__)


def convert_blob_to_base64(blob):
    if blob is not None:
        return base64.b64encode(blob).decode()
    return None


@work_hours_details_blueprint.route('/work_hours_details/<int:zeiteintrag_id>/<int:person_id>')
def show_details(zeiteintrag_id, person_id):
    if 'user_id' in session:
        user_role = session['user_role']
        if user_role == 'Steuerbüro' or user_role == 'Sachbearbeiter/Kostenträger':
            flash('Sie sind nicht berechtigt diese Seite aufzurufen.')
            return redirect(session['secure_url'])
        else:
            # Rückleitung bei unerlaubter Seite
            session['secure_url'] = url_for('work_hours_details.show_details', zeiteintrag_id=zeiteintrag_id,
                                            person_id=person_id)

            session['url'] = url_for('work_hours_details.show_details', zeiteintrag_id=zeiteintrag_id,
                                     person_id=person_id)
            # Datenbankaufrufe
            zeiteintrag_liste = get_zeiteintrag_by_id(zeiteintrag_id)
            zeiteintrag = zeiteintrag_liste[0]
            print(zeiteintrag)
            datum = zeiteintrag[3].strftime("%Y-%m-%d")
            von = zeiteintrag[3].strftime("%H:%M")
            bis = zeiteintrag[4].strftime("%H:%M")

            fahrten = get_fahrt_by_zeiteintrag(zeiteintrag_id)

            # Name Klient
            klient_id = zeiteintrag[6]
            klient_data = get_klient_data(klient_id)
            klient_name = klient_data[0][1] + ' ' + klient_data[0][2]

            # Überprüfung ob gebucht
            booked = check_booked(zeiteintrag_id)

            # Umwandlung Unterschriften
            if zeiteintrag[1]:
                unterschrift_mitarbeiter = convert_blob_to_base64(zeiteintrag[1])
            else:
                unterschrift_mitarbeiter = ""

            if zeiteintrag[2]:
                unterschrift_klient = convert_blob_to_base64(zeiteintrag[2])
            else:
                unterschrift_klient = ""

            return render_template('FMOF040_work_hours_details.html', zeiteintrag=zeiteintrag, fahrten=fahrten,
                                   klient_name=klient_name, datum=datum, von=von, bis=bis,
                                   unterschrift_klient=unterschrift_klient,
                                   unterschrift_mitarbeiter=unterschrift_mitarbeiter, zeiteintrag_id=zeiteintrag_id,
                                   person_id=person_id, booked=booked)

    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))
