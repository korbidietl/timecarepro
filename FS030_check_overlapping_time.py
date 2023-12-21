from flask import Blueprint, request, redirect, url_for, render_template
from db_query import check_for_overlapping_zeiteintrag


check_overlapping_time_blueprint = Blueprint('check_overlapping_time', __name__)

@check_overlapping_time_blueprint.route('/check_overlapping_time/<int:zeiteintrag_id>', methods=['GET', 'POST'])
def overlapping_time(zeiteintrag_id):

    overlapping_ids = check_for_overlapping_zeiteintrag(zeiteintrag_id, klient_id, start_time, end_time)
    overlapping_entries = []

    for id in overlapping_ids:
        entry_data = get_zeiteintrag_with_fahrten_by_id(id)
        overlapping_entries.append(entry_data)

    return render_template('popup.html', overlapping_entries=overlapping_entries,
                           original_zeiteintrag_id=zeiteintrag_id)


if __name__ == '__main__':
    app.run(debug=True)