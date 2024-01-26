import json

from model.database_connection import get_database_connection


# /FS010/
def save_change_log(person_id, table_type, old_state, new_state, entry_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    # Den alten Zustand als JSON-String speichern
    old_state_json = json.dumps(old_state)
    # Den neuen Zustand als JSON-String speichern
    new_state_json = json.dumps(new_state)
    # Die Änderungsprotokolle in der Datenbank speichern
    cursor.execute(
        "INSERT INTO protokoll (person_id, eintragungsart, eintrag_vorher, eintrag_nachher, eintrag_ID) VALUES (%s, %s, %s, %s, %s)",
        (person_id, table_type, old_state_json, new_state_json, entry_id))

    connection.commit()
    cursor.close()
    connection.close()


def get_protokoll(von=None, bis=None, aendernder_nutzer=None, eintrags_id=None):
    connection = get_database_connection()
    cursor = connection.cursor()
    query = """
        SELECT pk.ID, pk.zeit, CONCAT(p.vorname, ' ', p.nachname) AS Ändernder_Nutzer, pk.eintragungsart, 
        pk.eintrag_ID, pk.eintrag_vorher, pk.eintrag_nachher 
        FROM protokoll pk LEFT JOIN person p ON pk.person_ID = p.ID WHERE 1=1
    """
    parameters = []
    if von:
        query += " AND pk.zeit >= %s"
        parameters.append(von)
    if bis:
        query += " AND pk.zeit <= %s"
        parameters.append(bis)
    if aendernder_nutzer:
        query += " AND pk.person_id = %s"
        parameters.append(aendernder_nutzer)
    if eintrags_id:
        query += " AND pk.eintrag_id = %s"
        parameters.append(eintrags_id)

    query += " ORDER BY Zeit DESC"

    cursor.execute(query, parameters)
    return cursor.fetchall()
