from flask import Blueprint, render_template, session, url_for, request, Response, redirect, flash
import csv
import io


home_blueprint = Blueprint('home', __name__)


@home_blueprint.route('/home', methods=['POST', 'GET'])
def home():
    if 'user_id' in session:
        # Rückleitung bei unerlaubter Seite
        session['secure_url'] = url_for('home.home')

        # Auslesen aus Session und speicherung url für Rückleitung
        user_id = session.get('user_id')
        role = session.get('user_role')
        session['url'] = url_for('home.home')

        return render_template('FAN010_home.html', user_id=user_id, role=role)

    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))


@home_blueprint.route('/export-table', methods=['POST'])
def export_table():
    # Exportieren der Mitarbeitertabelle
    data = request.json['data']
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerows(data)
    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={'Content-disposition': 'attachment; '
                                                                                 'filename=exportierte_tabelle.csv'})
