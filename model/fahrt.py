from model.database_connection import get_database_connection


# /FMOF030/
# /FMOF050/
def add_fahrt(kilometer, start_adresse, end_adresse, abrechenbar, zeiteintrag_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO fahrt (kilometer, start_adresse, end_adresse, abrechenbar, zeiteintrag_ID) "
                   "VALUES (%s, %s, %s, %s, %s)", (kilometer, start_adresse, end_adresse, abrechenbar, zeiteintrag_id))
    connection.commit()
    fahrt_id = cursor.lastrowid
    cursor.close()
    connection.close()
    return fahrt_id


def create_placeholder_fahrt():
    connection = get_database_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO fahrt (kilometer, start_adresse, end_adresse, abrechenbar, zeiteintrag_ID) VALUES (0, '0', '0', 0, 1)")
        fahrt_id = cursor.lastrowid
        connection.commit()
        return fahrt_id

    except Exception as e:
        print(f"Fehler: {e}")
        connection.rollback()
        return None

    finally:
        cursor.close()
        connection.close()


# /FMOF040
# /FSK010/
def get_fahrt_by_zeiteintrag(zeiteintrag_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM fahrt WHERE zeiteintrag_ID = %s""",
                   (zeiteintrag_id,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


# /FMOF050/
def edit_fahrt(fahrt_id, kilometer, abrechenbar, zeiteintrag_id, start_adresse=None, end_adresse=None):
    connection = get_database_connection()
    cursor = connection.cursor()

    query = "UPDATE fahrt SET "
    parameters = []

    query += "kilometer = %s, "
    parameters.append(kilometer)

    if start_adresse is not None:
        query += "start_adresse = %s, "
        parameters.append(start_adresse)

    if end_adresse is not None:
        query += "end_adresse = %s, "
        parameters.append(end_adresse)

    query += "abrechenbar = %s, "
    parameters.append(abrechenbar)

    query += "zeiteintrag_ID = %s, "
    parameters.append(zeiteintrag_id)

    # remove last comma and space
    query = query[:-2]

    # add where clause
    query += " WHERE id = %s"
    parameters.append(fahrt_id)

    cursor.execute(query, parameters)
    connection.commit()
    cursor.close()
    connection.close()


# /FMOF050/
def delete_fahrt(fahrt_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM fahrt WHERE id = %s", (fahrt_id,))
    connection.commit()
    cursor.close()
    connection.close()


# /FMOF050
def get_highest_fahrt_id():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(ID) FROM fahrt")
    highest_id = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return 0 if highest_id is None else highest_id


def sum_km_monatlich(start_date, end_date, mitarbeiter_id=None, klient_id=None):
    connection = get_database_connection()
    cursor = connection.cursor()

    query = """
    SELECT EXTRACT(MONTH FROM z.start_zeit) AS Monat,
           SUM(f.kilometer) AS KM
    FROM zeiteintrag z
    JOIN fahrt f ON z.ID = f.zeiteintrag_ID
    WHERE z.start_zeit BETWEEN %s AND %s
    """

    conditions = []
    parameters = [start_date, end_date]

    if mitarbeiter_id:
        conditions.append("z.mitarbeiter_ID = %s")
        parameters.append(mitarbeiter_id)

    if klient_id:
        conditions.append("z.Klient_ID = %s")
        parameters.append(klient_id)

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " GROUP BY Monat ORDER BY Monat"

    cursor.execute(query, tuple(parameters))

    km_pro_monat = [0 for _ in range(12)]

    for row in cursor:
        monat_index = row[0] - 1
        km_pro_monat[monat_index] = row[1] if row[1] else 0

    # Werte außerhalb übergebenen Zeitraum 0.0
    start_monat = start_date.month
    end_monat = end_date.month
    for i in range(0, start_monat - 1):
        km_pro_monat[i] = 0
    for i in range(end_monat, 12):
        km_pro_monat[i] = 0

    return km_pro_monat


def fahrt_id_existing(fahrt_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM fahrt WHERE id = %s",
                   (fahrt_id,))
    result = cursor.fetchone()
    if result:
        return True
    return False


def fahrt_ids_list(zeiteintrag_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM fahrt WHERE zeiteintrag_ID = %s", (zeiteintrag_id,))
    result = [row[0] for row in cursor.fetchall()]  # Extrahiere nur die IDs aus dem Ergebnis
    cursor.close()
    connection.close()
    return result
