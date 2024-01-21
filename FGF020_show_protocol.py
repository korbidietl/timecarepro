from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, json, session, url_for, flash, redirect
from db_query import get_protokoll, person_dropdown

show_protocol_blueprint = Blueprint("show_protocol", __name__)


@show_protocol_blueprint.route('/show_protocol', methods=['GET', 'POST'])
def show_protocol():
    if 'user_id' in session:
        user_role = session['user_role']
        if user_role != 'Geschäftsführung':
            flash('Sie sind nicht berechtigt diese Seite aufzurufen.')
            return redirect(session['secure_url'])
        else:
            # Rückleitung bei unerlaubter Seite
            session['secure_url'] = url_for('show_protocol.show_protocol')

            # Ändernde Nutzer nur aus Verwaltung und Geschäftsführung
            nutzers = person_dropdown()
            if request.method == 'POST':
                # Auslesen übergebener Daten
                von = request.form.get('von')
                bis = request.form.get('bis')
                aendernder_nutzer = request.form.get('nutzer')
                eintrags_id = request.form.get('eintrags_id')

                # Bis um 1 Tag erhöhen damit akuteller angezeigt wird
                bis_datum = datetime.strptime(bis, '%Y-%m-%d') if isinstance(bis, str) else bis
                bis_datum += timedelta(days=1)
                bis_str = bis_datum.strftime('%Y-%m-%d')

                protocols = get_protokoll(von, bis_str, aendernder_nutzer, eintrags_id)
                entry = []

                for protocol in protocols:
                    json_string_alt = protocol[5].decode('utf-8')
                    data_dict_alt = json.loads(json_string_alt)

                    json_string_neu = protocol[5].decode('utf-8')
                    data_dict_neu = json.loads(json_string_neu)

                    entry.append((data_dict_alt, data_dict_neu))

                if not protocols:
                    return render_template('FGF020_show_protocol.html',
                                           protocols=[], nutzers=nutzers, von=von, bis=bis, nutzer=aendernder_nutzer,
                                           eintrags_id=eintrags_id)

                kombinierte_liste = zip(protocols, entry)
                return render_template('FGF020_show_protocol.html', kombinierte_liste=kombinierte_liste, nutzers=nutzers,
                                       von=von, bis=bis, nutzer=aendernder_nutzer, eintrags_id=eintrags_id)

            else:
                heute = datetime.now()

                # Das Datum auf den ersten Tag des aktuellen Monats setzen
                erster_des_monats = heute.replace(day=1)

                von = erster_des_monats.strftime('%Y-%m-%d')
                bis = heute.strftime('%Y-%m-%d')
                # Bis um 1 Tag erhöhen damit akuteller angezeigt wird
                bis_datum = datetime.strptime(bis, '%Y-%m-%d') if isinstance(bis, str) else bis
                bis_datum += timedelta(days=1)
                bis_str = bis_datum.strftime('%Y-%m-%d')

                protocols = get_protokoll(von, bis_str)
                entry = []
                for protocol in protocols:
                    json_string_alt = protocol[5].decode('utf-8')
                    data_dict_alt = json.loads(json_string_alt)

                    json_string_neu = protocol[6].decode('utf-8')
                    data_dict_neu = json.loads(json_string_neu)

                    entry.append((data_dict_alt, data_dict_neu))

                kombinierte_liste = zip(protocols, entry)
                return render_template('FGF020_show_protocol.html', kombinierte_liste=kombinierte_liste, nutzers=nutzers,
                                       von=von, bis=bis)

    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))
