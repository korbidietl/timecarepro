from flask import Blueprint, render_template, request, session
from db_query import get_client_table, get_client_table_sb, get_protokoll, person_dropdown

show_protocol_blueprint = Blueprint("show_protocol", __name__)


@show_protocol_blueprint.route('/show_protocol', methods=['GET', 'POST'])
def show_protocol():

    if request.method == 'POST':

        nutzers = person_dropdown()

        von = request.form.get('von')
        bis = request.form.get('bis')
        aendernder_nutzer = request.form.get('nutzer')
        eintrags_id = request.form.get('eintrags_id')

        protocols = get_protokoll(von, bis, aendernder_nutzer, eintrags_id)


        if not protocols:
            return render_template('FGF020_show_protocol.html',
                                   protocols=[], no_clients_message="Keine Protokolle vorhanden.")

        return render_template('FGF020_show_protocol.html', protocols=protocols, nutzers=nutzers)

    else:
        nutzers = person_dropdown()
        return render_template('FGF020_show_protocol.html', protocols=[], nutzers=nutzers)


