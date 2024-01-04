from flask import Blueprint, request, redirect, url_for, render_template
from db_query import check_for_overlapping_zeiteintrag, get_zeiteintrag_by_id, get_zeiteintrag_with_fahrten_by_id

check_overlapping_time_blueprint = Blueprint('check_overlapping_time', __name__)


@check_overlapping_time_blueprint.route('/check_overlapping_time/<int:zeiteintrag_id>', methods=['GET', 'POST'])
def overlapping_time(zeiteintrag_id):

    zeiteintrag_data = get_zeiteintrag_by_id(zeiteintrag_id)

    if zeiteintrag_data:
        # Extrahieren der benötigten Daten aus dem ersten Ergebnis
        einzelner_zeiteintrag = zeiteintrag_data[0]
        klient_id = einzelner_zeiteintrag[6]
        startzeit = einzelner_zeiteintrag[3]
        endzeit = einzelner_zeiteintrag[4]

    overlapping_ids = check_for_overlapping_zeiteintrag(zeiteintrag_id, klient_id, startzeit, endzeit)
    overlapping_entries = []

    for id in overlapping_ids:
        entry_data = get_zeiteintrag_with_fahrten_by_id(id)
        overlapping_entries.append(entry_data)

    return render_template('popup.html', overlapping_entries=overlapping_entries,
                           original_zeiteintrag_id=zeiteintrag_id)
