from flask import Blueprint, render_template

work_hours_details_blueprint = Blueprint('work_hours_details',__name__)


@work_hours_details_blueprint.route('/work_hours_details/<int:zeiteintrag_id>')
def show_details(zeiteintrag_id):
    # Datenbankaufrufe
    # zeiteintrag = get_zeiteintrag_details(zeiteintrag_id)
    # fahrten =
    return render_template('FMOF040_work_hours_details.html') # fahrten=fahrten, zeiteintrag=zeiteintrag)
