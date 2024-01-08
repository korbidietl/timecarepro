import csv
import io

from flask import Blueprint, render_template, session, url_for, request, Response

home_blueprint = Blueprint('home', __name__)


@home_blueprint.route('/home', methods=['POST', 'GET'])
def home():
    user_id = session.get('user_id')
    role = session.get('user_role')
    session['url'] = url_for('home.home')

    return render_template('FAN010_home.html', user_id=user_id, role=role)


@home_blueprint.route('/export-table', methods=['POST'])
def export_table():
    data = request.json['data']
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerows(data)
    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={'Content-disposition': 'attachment; filename=exportierte_tabelle.csv'})
