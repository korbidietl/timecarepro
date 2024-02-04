import datetime
from flask import session
from model.database_connection import get_database_connection


# /FS030/
# /FMOF010/
# /FMOF030/
# /FSK010/
def check_for_overlapping_zeiteintrag(zeiteintrag_id, start_time, end_time):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id FROM zeiteintrag WHERE id != %s "
        "AND ((start_zeit >= %s AND start_zeit < %s) "
        "OR (end_zeit > %s AND end_zeit <= %s) "
        "OR (start_zeit <= %s AND end_zeit >= %s))",
        (zeiteintrag_id, start_time, end_time, start_time, end_time, start_time, end_time))
    ids = [id[0] for id in cursor.fetchall()]
    cursor.close()
    connection.close()
    return ids


# /FAN030/
def get_zeiteintrag_for_mitarbeiter(mitarbeiter_id, month, year):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            z.ID AS Zeiteintragnr,
            DATE_FORMAT(z.start_zeit, '%d.%m.%Y') AS Datum,
            DATE_FORMAT(z.start_zeit, '%H:%i') AS Anfang,
            DATE_FORMAT(z.end_zeit, '%H:%i') AS Ende
        FROM
            zeiteintrag z
            LEFT JOIN person p ON z.mitarbeiter_ID = p.id
        WHERE
            z.mitarbeiter_ID = %s AND
            MONTH(z.start_zeit) = %s AND
            YEAR(z.start_zeit) = %s
        GROUP BY
            z.id
    """, (mitarbeiter_id, month, year))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


# /FMOF010/
def get_zeiteintrag_for_client_and_person(client_id, person_id, month, year):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            z.ID AS Zeiteintragnr,
            DATE_FORMAT(z.start_zeit, '%d.%m.%Y') AS Datum,
            z.beschreibung AS Beschreibung,
            SUM(f.kilometer) AS Kilometer,
            DATE_FORMAT(z.start_zeit, '%H:%i') AS Anfang,
            DATE_FORMAT(z.end_zeit, '%H:%i') AS Ende,
            DATE_FORMAT(TIMEDIFF(end_zeit, start_zeit),'%H:%i') AS dauer,
            CONCAT(p.vorname, ' ', p.nachname) AS Mitarbeiter,
            p.id AS Mitarbeiter_id,
            z.unterschrift_Klient AS Unterschrift_Klient,
            z.unterschrift_Mitarbeiter AS Unterschrift_Mitarbeiter
        FROM
            zeiteintrag z
            LEFT JOIN fahrt f ON z.id = f.zeiteintrag_id
            LEFT JOIN person p ON z.mitarbeiter_ID = p.id
        WHERE
            z.klient_ID = %s AND
            p.ID = %s AND
            MONTH(z.start_zeit) = %s AND
            YEAR(z.start_zeit) = %s
        GROUP BY
            z.id
    """, (client_id, person_id, month, year))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


# /FMOF010/
def get_zeiteintrag_for_client(client_id, month, year):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
            SELECT
                z.ID AS Zeiteintragnr,
                DATE_FORMAT(z.start_zeit, '%d.%m.%Y') AS Datum,
                z.beschreibung AS Beschreibung,
                SUM(f.kilometer) AS Kilometer,
                DATE_FORMAT(z.start_zeit, '%H:%i') AS Anfang,
                DATE_FORMAT(z.end_zeit, '%H:%i') AS Ende,
                DATE_FORMAT(TIMEDIFF(end_zeit, start_zeit),'%H:%i') AS dauer,
                CONCAT(p.vorname, ' ', p.nachname) AS Mitarbeiter,
                p.id AS Mitarbeiter_id,
                z.unterschrift_Klient AS Unterschrift_Klient,
                z.unterschrift_Mitarbeiter AS Unterschrift_Mitarbeiter
            FROM
                zeiteintrag z
                LEFT JOIN fahrt f ON z.id = f.zeiteintrag_id
                LEFT JOIN person p ON z.mitarbeiter_ID = p.id
            WHERE
                z.klient_ID = %s AND            
                MONTH(z.start_zeit) = %s AND
                YEAR(z.start_zeit) = %s
            GROUP BY
                z.id
        """, (client_id, month, year))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


# /FMOF010/
# /FMOF020/
# /FGF030/
# /FSK010/
def check_booked(zeiteintrag_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
    SELECT 1
    FROM zeiteintrag z
    JOIN klient k ON z.klient_id = k.id
    JOIN buchung b ON b.klient_id = k.id
    WHERE z.id = %s
    AND EXTRACT(MONTH FROM b.monat) = EXTRACT(MONTH FROM z.end_zeit)
    LIMIT 1
    """, (zeiteintrag_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result:
        return True
    return False


# /FMOF020/
def get_zeiteintrag_for_person(person_id, month, year):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            z.ID AS Zeiteintragnr,
            DATE_FORMAT(z.start_zeit, '%d.%m.%Y') AS Datum,
            z.beschreibung AS Tätigkeit,
            SUM(f.kilometer) AS Kilometer,
            DATE_FORMAT(z.start_zeit, '%H:%i') AS Anfang,
            DATE_FORMAT(z.end_zeit, '%H:%i') AS Ende,
            CONCAT(k.vorname, ' ', k.nachname) AS Klient,
            z.unterschrift_Klient AS Unterschrift_Klient,
            z.unterschrift_Mitarbeiter AS Unterschrift_Mitarbeiter
        FROM
            zeiteintrag z
            LEFT JOIN fahrt f ON z.ID = f.zeiteintrag_ID
            LEFT JOIN klient k ON z.klient_ID = k.ID
            LEFT JOIN person p ON z.mitarbeiter_ID = p.ID
        WHERE
            p.ID = %s AND
            MONTH(z.start_zeit) = %s AND
            YEAR(z.start_zeit) = %s
        GROUP BY
            z.id
    """, (person_id, month, year))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


# /FMOF030/
def add_zeiteintrag(unterschrift_mitarbeiter, unterschrift_klient, start_time, end_time,
                    klient_id, fachkraft, beschreibung, interne_notiz, absage):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO zeiteintrag (unterschrift_Mitarbeiter, unterschrift_Klient, start_zeit, end_zeit, "
                   "mitarbeiter_ID, klient_ID, fachkraft, beschreibung, interne_notiz, absage) "
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                   (unterschrift_mitarbeiter, unterschrift_klient, start_time, end_time, session['user_id'],
                    klient_id, fachkraft, beschreibung, interne_notiz, absage))
    zeiteintrag_id = cursor.lastrowid
    connection.commit()
    cursor.close()
    connection.close()
    return zeiteintrag_id


# /FMOF030/
# /FMOF050/
def is_booked_client(client_id, monat, jahr):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
    SELECT 1
    FROM zeiteintrag z
    JOIN klient k ON z.klient_id = k.id
    JOIN buchung b ON b.klient_id = k.id
    WHERE k.id = %s
    AND EXTRACT(MONTH FROM b.monat) = %s
    AND EXTRACT(YEAR FROM b.monat) = %s
    LIMIT 1
    """, (client_id, monat, jahr))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result:
        return True
    return False


# /FMOF040/
def get_zeiteintrag_by_id(zeiteintrag_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM zeiteintrag WHERE ID = %s""",
                   (zeiteintrag_id,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


# /FMOF050/
# /FV100/
def edit_zeiteintrag(zeiteintrag_id, start_time=None, end_time=None, unterschrift_mitarbeiter=None,
                     unterschrift_klient=None, klient_id=None, fachkraft=None,
                     beschreibung=None, interne_notiz=None, absage=None):
    connection = get_database_connection()
    cursor = connection.cursor()
    if unterschrift_mitarbeiter not in [None, ""] and unterschrift_klient not in [None, ""]:
        cursor.execute("UPDATE zeiteintrag SET start_zeit = %s, end_zeit = %s, unterschrift_Mitarbeiter = %s, "
                       "unterschrift_Klient = %s, klient_ID = %s, fachkraft = %s, "
                       "beschreibung = %s, interne_notiz = %s, absage = %s "
                       "WHERE ID = %s",
                       (start_time, end_time, unterschrift_mitarbeiter, unterschrift_klient, klient_id, fachkraft,
                        beschreibung, interne_notiz, absage, zeiteintrag_id))
    elif unterschrift_mitarbeiter not in [None, ""] and unterschrift_klient in [None, ""]:
        cursor.execute("UPDATE zeiteintrag SET start_zeit = %s, end_zeit = %s, unterschrift_Mitarbeiter = %s, "
                       "unterschrift_Klient = NULL, klient_ID = %s, fachkraft = %s, "
                       "beschreibung = %s, interne_notiz = %s, absage = %s "
                       "WHERE ID = %s",
                       (start_time, end_time, unterschrift_mitarbeiter, klient_id, fachkraft,
                        beschreibung, interne_notiz, absage, zeiteintrag_id))
    else:
        cursor.execute("UPDATE zeiteintrag SET start_zeit = %s, end_zeit = %s, unterschrift_Mitarbeiter = NULL, "
                       "unterschrift_Klient = NULL, klient_ID = %s, fachkraft = %s, "
                       "beschreibung = %s, interne_notiz = %s, absage = %s "
                       "WHERE ID = %s",
                       (start_time, end_time, klient_id, fachkraft,
                        beschreibung, interne_notiz, absage, zeiteintrag_id))
    connection.commit()
    cursor.close()
    connection.close()


# /FMOF060/
# /FV110/
def delete_zeiteintrag(zeiteintrag_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM fahrt WHERE zeiteintrag_ID = %s", (zeiteintrag_id,))
    cursor.execute("DELETE FROM zeiteintrag WHERE id = %s", (zeiteintrag_id,))
    connection.commit()
    cursor.close()
    connection.close()


def get_email_by_zeiteintrag(zeiteintrag_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT person.email FROM person INNER JOIN zeiteintrag ON person.ID = zeiteintrag.mitarbeiter_id "
                   "WHERE zeiteintrag.ID = %s", (zeiteintrag_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None


def check_and_return_signatures(client_id, month, year):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
       SELECT id, unterschrift_Klient, unterschrift_Mitarbeiter FROM zeiteintrag 
       WHERE klient_ID = %s AND MONTH(end_zeit) = %s AND YEAR(end_zeit) = %s
    """, (client_id, month, year))
    results = cursor.fetchall()
    missing_signatures = []

    for result in results:
        missing = []
        # Wenn die Klient-ID gleich 1 ist, wird nur die Mitarbeiter-Unterschrift überprüft
        if client_id == 1:
            if not result[2]:  # Überprüfen, ob die Unterschrift des Mitarbeiters fehlt
                missing.append('Mitarbeiter')
        else:
            # Für alle anderen Klienten werden beide Unterschriften überprüft
            if not result[1]:  # Überprüfen, ob die Unterschrift des Klienten fehlt
                missing.append('Klient')
            if not result[2]:  # Überprüfen, ob die Unterschrift des Mitarbeiters fehlt
                missing.append('Mitarbeiter')

        if missing:
            missing_signatures.append({'id': result[0], 'missing': missing})

    if missing_signatures:
        return missing_signatures  # Rückgabe der Liste der IDs, bei denen Signaturen fehlen

    return True  # Alle Signaturen sind vorhanden


def get_first_te(client_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT DATE_FORMAT(start_zeit, '%Y-%m') AS StartMonat
        FROM zeiteintrag 
        WHERE klient_ID = %s 
        ORDER BY start_zeit ASC 
        LIMIT 1
    """, (client_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result:
        # Das Ergebnis ist ein Tuple, das den Monat und das Jahr im Format 'YYYY-MM' enthält
        return result[0]  # Rückgabe des ersten Elements im Tuple
    else:
        return None  # Keine Zeiteinträge gefunden


def check_signatures(client_id, month, year):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
       SELECT zeiteintrag.ID, unterschrift_Klient, unterschrift_Mitarbeiter 
       FROM zeiteintrag 
       WHERE Klient_ID = %s AND MONTH(end_zeit) = %s AND YEAR(end_zeit) = %s
   """, (client_id, month, year))
    results = cursor.fetchall()
    missing_signatures = []

    if not results:
        return False, missing_signatures

    all_signed = True
    for result in results:
        if result['unterschrift_Klient'] is None or result['unterschrift_Mitarbeiter'] is None:
            all_signed = False
            missing = []
            if result['unterschrift_Klient'] is None:
                missing.append('Klient')
            if result['unterschrift_Mitarbeiter'] is None:
                missing.append('Mitarbeiter')
            missing_signatures.append({'zeiteintrag_id': result['ID'], 'missing': missing})

    return all_signed, missing_signatures


def book_zeiteintrag(client_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM buchung 
        WHERE Klient_ID = %s ORDER BY monat DESC LIMIT 1
    """, (client_id,))
    last_entry = cursor.fetchone()
    if not last_entry:
        next_month_to_book = get_first_te(client_id)
        end_year, end_month = map(int, next_month_to_book.split('-'))
    else:
        start_month = last_entry[2].month
        start_year = last_entry[2].year
        end_month = start_month + 1
        if end_month == 13:
            end_month = 1
            end_year = start_year + 1
        else:
            end_year = start_year
    cursor.execute("""
        SELECT * FROM zeiteintrag 
        WHERE Klient_ID = %s AND MONTH(end_zeit) = %s AND YEAR(end_zeit) = %s
    """, (client_id, end_month, end_year))
    results = cursor.fetchall()
    if not results:
        return False
    cursor.execute("""
            SELECT * FROM klient 
            WHERE ID = %s
        """, (client_id,))
    client = cursor.fetchone()
    if not client:
        return False

    fk_hours = 0
    hk_hours = 0
    saldo_fk = 0
    saldo_hk = 0

    if client[7] is not None:  # Wenn FK-Kontingent vorhanden ist
        saldo_fk = client[7]  # Startwert ist das FK-Kontingent

    if client[8] is not None:  # Wenn HK-Kontingent vorhanden ist
        saldo_hk = client[8]  # Startwert ist das HK-Kontingent

    cursor.execute("""
            SELECT * FROM zeiteintrag 
            WHERE Klient_ID = %s AND MONTH(end_zeit) = %s AND YEAR(end_zeit) = %s
        """, (client_id, end_month, end_year))
    results = cursor.fetchall()

    if not results:
        return False

    for result in results:
        if result[7] == 1 and saldo_fk is not None:  # Nur FK-Stunden von FK-Kontingent abziehen
            fk_hours += result[4].hour - result[3].hour

        if result[7] == 0 and saldo_hk is not None:  # Nur HK-Stunden von HK-Kontingent abziehen
            hk_hours += result[4].hour - result[3].hour

    if saldo_fk is not None:
        saldo_fk -= fk_hours

    if saldo_hk is not None:
        saldo_hk -= hk_hours

    monat = datetime.date(end_year, end_month, 1)
    cursor.execute("""
            INSERT INTO buchung (Klient_ID, monat, saldo_FK, saldo_HK)
            VALUES (%s, %s, %s, %s)
        """, (client_id, monat, saldo_fk, saldo_hk))
    connection.commit()
    return True


def get_report_zeiteintrag(date_from, date_to, client_id=None, mitarbeiter_id=None):
    connection = get_database_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            CONCAT(Mitarbeiter.vorname, ' ', Mitarbeiter.nachname) AS Mitarbeiter,
            CONCAT(Sachbearbeiter.vorname, ' ', Sachbearbeiter.nachname) AS Sachbearbeiter, 
            CONCAT(klient.vorname, ' ', klient.nachname) AS Klient,
            TIME_FORMAT(SEC_TO_TIME(SUM(TIMESTAMPDIFF(MINUTE, zeiteintrag.start_zeit, zeiteintrag.end_zeit) * 60)), '%H:%i') AS geleistete_stunden,
            SUM(fahrt.kilometer) AS gefahrene_kilometer,
            SUM(CASE WHEN fahrt.abrechenbar THEN fahrt.kilometer ELSE 0 END) AS abrechenbare_km,
            SUM(CASE WHEN fahrt.abrechenbar THEN 0 ELSE fahrt.kilometer END) AS nicht_abrechenbare_km,
            SUM(CASE WHEN zeiteintrag.Absage THEN 1 ELSE 0 END) AS Absage
        FROM
            zeiteintrag
        INNER JOIN person AS Mitarbeiter ON zeiteintrag.mitarbeiter_id = Mitarbeiter.id
        INNER JOIN klient ON zeiteintrag.klient_id = klient.id
        INNER JOIN person AS Sachbearbeiter ON klient.sachbearbeiter_id = Sachbearbeiter.id
        LEFT JOIN fahrt ON zeiteintrag.id = fahrt.zeiteintrag_id
        WHERE
            zeiteintrag.start_zeit >= %s AND
            zeiteintrag.start_zeit < %s
    """
    params = [date_from, date_to]

    if client_id is not None and mitarbeiter_id is not None:
        query += " AND klient.id = %s AND Mitarbeiter.id = %s"
        params += [client_id, mitarbeiter_id]
    elif client_id is not None:
        query += " AND klient.id = %s"
        params.append(client_id)
    elif mitarbeiter_id is not None:
        query += " AND Mitarbeiter.id = %s"
        params.append(mitarbeiter_id)

    # Fügen Sie diese Zeile außerhalb der if-elif-Blöcke hinzu
    query += " GROUP BY Mitarbeiter.id, Sachbearbeiter.id, klient.id"

    cursor.execute(query, tuple(params))
    return cursor.fetchall()


def get_report_mitarbeiter(date_from, date_to, client_id=None, mitarbeiter_id=None):
    connection = get_database_connection()
    cursor = connection.cursor()
    query = """
        SELECT
            Mitarbeiter.id, 
            Mitarbeiter.nachname,
            Mitarbeiter.vorname,
            TIME_FORMAT(SEC_TO_TIME(SUM(TIMESTAMPDIFF(MINUTE, zeiteintrag.start_zeit, zeiteintrag.end_zeit) * 60)), '%H:%i') AS geleistete_stunden,
            SUM(fahrt.kilometer) AS gefahrene_kilometer,
            SUM(CASE WHEN fahrt.abrechenbar THEN fahrt.kilometer ELSE 0 END) AS abrechenbare_km,
            SUM(CASE WHEN fahrt.abrechenbar THEN 0 ELSE fahrt.kilometer END) AS nicht_abrechenbare_km,
            SUM(CASE WHEN zeiteintrag.Absage THEN 1 ELSE 0 END) AS Absage
        FROM
            zeiteintrag
        INNER JOIN person AS Mitarbeiter ON zeiteintrag.mitarbeiter_id = Mitarbeiter.id
        LEFT JOIN fahrt ON zeiteintrag.id = fahrt.zeiteintrag_id
        WHERE
            zeiteintrag.start_zeit >= %s AND
            zeiteintrag.start_zeit < %s
    
    """
    params = [date_from, date_to]

    if mitarbeiter_id is not None:
        query += " AND Mitarbeiter.id = %s"
        params.append(mitarbeiter_id)

    elif client_id is not None:
        query += " AND zeiteintrag.klient_id = %s"
        params.append(client_id)

    query += " GROUP BY Mitarbeiter.ID  ORDER BY Mitarbeiter.ID  ASC"
    cursor.execute(query, tuple(params))
    return cursor.fetchall()


def sum_mitarbeiter(month, year):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT DISTINCT Mitarbeiter_ID FROM zeiteintrag 
        WHERE MONTH(end_zeit) = %s AND YEAR(end_zeit) = %s 
        AND Mitarbeiter_ID IN (SELECT ID FROM person WHERE sperre = FALSE)
    """, (month, year))
    mitarbeiter_ids = cursor.fetchall()
    return len(mitarbeiter_ids)


def sum_hours_tabelle(start_date, end_date, client_id, user_id):
    connection = get_database_connection()
    cursor = connection.cursor()

    query = """
     SELECT 
         TIME_FORMAT(SEC_TO_TIME(SUM(TIMESTAMPDIFF(MINUTE, z.start_zeit, z.end_zeit) * 60)), '%H:%i') AS anzahl_Stunden
     FROM zeiteintrag z
     WHERE z.end_zeit BETWEEN %s AND %s
     """
    params = [start_date, end_date]

    if user_id and client_id:
        query += " AND z.mitarbeiter_ID = %s AND z.Klient_ID = %s"
        params.extend([user_id, client_id])
    elif user_id:
        query += " AND z.mitarbeiter_ID = %s"
        params.append(user_id)
    elif client_id:
        query += " AND z.Klient_ID = %s"
        params.append(client_id)

    cursor.execute(query, params)

    result = cursor.fetchone()
    return result[0] if result else "00:00"


def monatliche_gesamtstunden(start_date, end_date, mitarbeiter_id=None, klient_id=None):
    connection = get_database_connection()
    cursor = connection.cursor()

    query = """
    SELECT EXTRACT(MONTH FROM z.start_zeit) AS Monat, 
        COALESCE(
           ROUND(
                SUM(
                    HOUR(TIMEDIFF(z.end_zeit, z.start_zeit)) + 
                    MINUTE(TIMEDIFF(z.end_zeit, z.start_zeit)) / 60.0
                ), 2
            ), 0.0
        ) AS gesamtstunden
    FROM zeiteintrag z
    """

    where_clauses = ["z.start_zeit BETWEEN %s AND %s"]
    params = [start_date, end_date]

    if mitarbeiter_id:
        where_clauses.append("z.mitarbeiter_ID = %s")
        params.append(mitarbeiter_id)

    if klient_id:
        where_clauses.append("z.Klient_ID = %s")
        params.append(klient_id)

    query += " WHERE " + " AND ".join(where_clauses)
    query += " GROUP BY Monat ORDER BY Monat"

    cursor.execute(query, tuple(params))
    results = cursor.fetchall()

    # Erstellen einer Liste mit 12 Elementen für jeden Monat des Jahres
    monatliche_stunden = [0.0] * 12
    for row in results:
        monat, stunden = row
        monatliche_stunden[monat - 1] = stunden  # Monate sind 1-basiert, Listen sind 0-basiert

    # Werte außerhalb übergebenen Zeitraum 0.0
    start_monat = start_date.month
    end_monat = end_date.month
    for i in range(0, start_monat - 1):
        monatliche_stunden[i] = 0.0
    for i in range(end_monat, 12):
        monatliche_stunden[i] = 0.0

    return monatliche_stunden


def sum_absage_tabelle(start_date, end_date, client_id, user_id=None):
    connection = get_database_connection()
    cursor = connection.cursor()

    query = """
        SELECT COUNT(z.ID) AS anzahl_Absagen
        FROM zeiteintrag z
        WHERE z.end_zeit BETWEEN %s AND %s AND z.absage = 1
        """
    params = [start_date, end_date]

    if user_id and client_id:
        query += " AND z.mitarbeiter_ID = %s AND z.Klient_ID = %s"
        params.extend([user_id, client_id])
    elif user_id:
        query += " AND z.mitarbeiter_ID = %s"
        params.append(user_id)
    elif client_id:
        query += " AND z.Klient_ID = %s"
        params.append(client_id)

    cursor.execute(query, params)

    result = cursor.fetchone()
    return result[0] if result else 0


def sum_absagen_monatlich(start_date, end_date, mitarbeiter_id=None, klient_id=None):
    connection = get_database_connection()
    cursor = connection.cursor()

    query = """
    SELECT EXTRACT(MONTH FROM z.start_zeit) AS Monat, COUNT(z.ID) AS anzahl_Absagen
    FROM zeiteintrag z 
    WHERE z.absage = 1
    AND z.start_zeit BETWEEN %s AND %s
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

    absagen_pro_monat = [0] * 12  # Initialisiere eine Liste mit 12 Elementen für jeden Monat
    for row in cursor:
        monat_index = row[0] - 1  # Der Monatindex (Januar=0, Februar=1, ...)
        absagen_pro_monat[monat_index] = row[1]

    # Werte außerhalb übergebenen Zeitraum 0.0
    start_monat = start_date.month
    end_monat = end_date.month
    for i in range(0, start_monat - 1):
        absagen_pro_monat[i] = 0
    for i in range(end_monat, 12):
        absagen_pro_monat[i] = 0

    return absagen_pro_monat


def sum_km_monatlich_tabelle(start_date, end_date, klient_id=None, mitarbeiter_id=None):
    connection = get_database_connection()
    cursor = connection.cursor()

    query = """
        SELECT 
            SUM(f.kilometer) AS gesamt_km,
            SUM(IF(f.abrechenbar = 1, f.kilometer, 0)) AS abrechenbare_km,
            SUM(IF(f.abrechenbar = 0, f.kilometer, 0)) AS nicht_abrechenbare_km
        FROM zeiteintrag z
        JOIN fahrt f ON z.ID = f.zeiteintrag_ID
        WHERE z.start_zeit BETWEEN %s AND %s
        """
    params = [start_date, end_date]

    if mitarbeiter_id and klient_id:
        query += " AND z.mitarbeiter_ID = %s AND z.Klient_ID = %s"
        params.extend([mitarbeiter_id, klient_id])
    elif mitarbeiter_id:
        query += " AND z.mitarbeiter_ID = %s"
        params.append(mitarbeiter_id)
    elif klient_id:
        query += " AND z.Klient_ID = %s"
        params.append(klient_id)

    cursor.execute(query, params)

    result = cursor.fetchone()
    if result:
        return {
            'gesamt_km': result[0] if result[0] else 0,
            'abrechenbare_km': result[1] if result[1] else 0,
            'nicht_abrechenbare_km': result[2] if result[2] else 0
        }
    else:
        return {'gesamt_km': 0, 'abrechenbare_km': 0, 'nicht_abrechenbare_km': 0}


def get_zeiteintrag_id(person_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM zeiteintrag WHERE mitarbeiter_ID = %s", (person_id,))
    result = cursor.fetchall()
    return result


def get_zeiteintrag_with_fahrten_by_id(zeiteintrag_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""SELECT ze.*, fa.* FROM zeiteintrag ze 
        LEFT JOIN fahrt fa ON ze.id = fa.zeiteintrag_id WHERE ze.id = %s""",
                   (zeiteintrag_id,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()

    # Group the result by Zeiteintrag entries
    zeiteintrag_fahrten = {}
    for row in result:
        zeiteintrag_id = row[0]
        if zeiteintrag_id not in zeiteintrag_fahrten:
            zeiteintrag_fahrten[zeiteintrag_id] = {'zeiteintrag': row[:8], 'fahrten': []}
        zeiteintrag_fahrten[zeiteintrag_id]['fahrten'].append(row[8:])

    return list(zeiteintrag_fahrten.values())  # Die Ergebnisse werden dann nach Zeiteintrag-IDs gruppiert.
