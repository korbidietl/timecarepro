from flask import Blueprint, render_template, request, session
from db_query import get_client_table, get_client_table_sb, get_protokoll, person_dropdown

show_protocol_blueprint = Blueprint("show_protocol", __name__)


@show_protocol_blueprint.route('/show_protocol', methods=['GET', 'POST'])
def show_protocol():

    if request.method == 'POST':
        von = request.form['von']
        bis = request.form['bis']
        aendernder_nutzer = request.form['nutzer']
        eintrags_id = request.form['eintrags_id']

        protocols = get_protokoll(von, bis, aendernder_nutzer, eintrags_id)

        nutzers = person_dropdown()
        nutzer = {'nutzers': nutzers}

        if not protocols:
            return render_template('FGF020_show_protocol.html',
                                   protocols=[], no_clients_message="Keine Protokolle vorhanden.")

        return render_template('FGF020_show_protocol.html', protocols=protocols, **nutzer)

    else:
        nutzers = person_dropdown()
        nutzer = {'nutzers': nutzers}
        return render_template('FGF020_show_protocol.html', protocols=[], **nutzer)


