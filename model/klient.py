import datetime

from model.database_connection import get_database_connection
from model.buchung import check_month_booked


# /FS010/
def get_current_client(client_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM klient WHERE ID = %s", (client_id,))
    result = cursor.fetchone()
    # Überprüfen, ob ein Ergebnis vorliegt
    if result is None:
        return None
        cursor.close()
        connection.close()

    # Wandeln Sie das Ergebnis in ein Dictionary um
    old_state = {}
    for column_description, value in zip(cursor.description, result):
        key = column_description[0]  # Der Name der Spalte
        if isinstance(value, datetime.date):
            # Datumswerte konvertieren
            old_state[key] = value.isoformat()
        else:
            old_state[key] = value

    cursor.close()
    connection.close()
    return old_state


# /FS010/
def get_new_client(client_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM klient WHERE ID = %s", (client_id,))
    result = cursor.fetchone()
    if result is None:
        return None
        cursor.close()
        connection.close()

    # Wandeln Sie das Ergebnis in ein Dictionary um
    new_state = {}
    for column_description, value in zip(cursor.description, result):
        key = column_description[0]  # Der Name der Spalte
        if isinstance(value, datetime.date):
            # Datumswerte konvertieren
            new_state[key] = value.isoformat()
        else:
            new_state[key] = value

    cursor.close()
    connection.close()
    return new_state


# /FAN030/
def get_unbooked_clients_for_month(monat, year):
    # Connect to the database
    connection = get_database_connection()
    cursor = connection.cursor()

    # Retrieve all time entries for the specified month and year, along with client details
    cursor.execute("SELECT z.start_zeit, z.klient_ID, k.vorname, k.nachname "
                   "FROM zeiteintrag z "
                   "JOIN klient k ON z.klient_ID = k.ID "
                   "WHERE EXTRACT(MONTH FROM z.start_zeit) = %s AND EXTRACT(YEAR FROM z.start_zeit) = %s",
                   (monat, year,))

    # Dictionary to track the booking status of each client
    unbooked_clients = {}

    # Iterate over each time entry
    for start_zeit, klient_id, vorname, nachname in cursor.fetchall():
        # Check if the client is already booked for the month
        if not check_month_booked(start_zeit, klient_id):
            # If not, add them to the unbooked clients list
            if klient_id not in unbooked_clients:
                unbooked_clients[klient_id] = {'vorname': vorname, 'nachname': nachname}

    # Return None if unbooked_clients is empty, else return the list of unbooked clients
    if not unbooked_clients:
        return None
    else:
        unbooked_clients_list = [(klient_id, client['vorname'], client['nachname'], monat, year)
                                 for klient_id, client in unbooked_clients.items()]
        return unbooked_clients_list


# /FAN040/
def get_client_table_sb(person_id, month, year):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
            SELECT 
                k.ID, 
                k.nachname, 
                k.vorname,
                k.kontingent_FK, 
                k.kontingent_HK,
                COALESCE(k.kontingent_FK - SUM(CASE WHEN z.fachkraft = 1 THEN 
                TIMESTAMPDIFF(HOUR, z.start_zeit, z.end_zeit) ELSE 0 END), k.kontingent_FK) * -1 as fachkraftsaldo,
                COALESCE(k.kontingent_HK - SUM(CASE WHEN z.fachkraft = 0 THEN 
                TIMESTAMPDIFF(HOUR, z.start_zeit, z.end_zeit) ELSE 0 END), k.kontingent_HK) * -1 as hilfskraftsaldo,
                CONCAT(p.vorname, ' ', p.nachname) AS Fallverantwortung
            FROM 
                klient k
            LEFT JOIN 
                zeiteintrag z ON k.ID = z.klient_id AND MONTH(z.start_zeit) = %s AND YEAR(z.start_zeit) = %s
            LEFT JOIN 
                person p ON k.fallverantwortung_ID = p.ID
            WHERE 
                k.sachbearbeiter_ID = %s
            GROUP BY 
                k.ID, p.nachname, p.vorname
            ORDER BY k.ID ASC
        """, (month, year, person_id))
    client_info = cursor.fetchall()
    cursor.close()
    return client_info


# /FAN040/
def get_client_table(month, year):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
           SELECT 
               k.ID, 
               k.nachname, 
               k.vorname,
               k.kontingent_FK, 
               k.kontingent_HK,
               COALESCE(k.kontingent_FK - SUM(CASE WHEN z.fachkraft = 1 THEN 
               TIMESTAMPDIFF(HOUR, z.start_zeit, z.end_zeit) ELSE 0 END), k.kontingent_FK) * -1 as fachkraftsaldo,
               COALESCE(k.kontingent_HK - SUM(CASE WHEN z.fachkraft = 0 THEN 
               TIMESTAMPDIFF(HOUR, z.start_zeit, z.end_zeit) ELSE 0 END), k.kontingent_HK) * -1 as hilfskraftsaldo,
               CONCAT(p.vorname, ' ', p.nachname) AS Fallverantwortung
           FROM 
               klient k
           LEFT JOIN 
               zeiteintrag z ON k.ID = z.klient_id AND MONTH(z.start_zeit) = %s AND YEAR(z.start_zeit) = %s
           LEFT JOIN 
               person p ON k.fallverantwortung_ID = p.ID
           GROUP BY 
               k.ID, p.nachname, p.vorname
            ORDER BY k.ID ASC
       """, (month, year))
    client_info = cursor.fetchall()
    cursor.close()
    return client_info


# /FMOF010/
def sum_hours_klient(klient_id, month, year, mitarbeiter_id=None):
    connection = get_database_connection()
    cursor = connection.cursor()

    query = """
        SELECT k.ID AS Klient_ID, k.Vorname, k.Nachname, 
        TIME_FORMAT(SEC_TO_TIME(SUM(TIMESTAMPDIFF(MINUTE, z.start_zeit, z.end_zeit) * 60)), '%H:%i') AS anzahl_Stunden 
        FROM klient k 
        JOIN zeiteintrag z ON k.ID = z.Klient_ID 
        WHERE k.ID = %s AND MONTH(z.end_zeit) = %s AND YEAR(z.end_zeit) = %s
    """

    params = [klient_id, month, year]

    # Optional: Filtern nach Mitarbeiter-ID, wenn eine solche übergeben wird
    if mitarbeiter_id:
        query += " AND z.mitarbeiter_id = %s"
        params.append(mitarbeiter_id)

    query += " GROUP BY k.ID ORDER BY k.ID"

    cursor.execute(query, params)
    return cursor.fetchall()


# /FMOF010/
def sum_km_klient_ges(klient_id, month, year, mitarbeiter_id=None):
    connection = get_database_connection()
    cursor = connection.cursor()

    query = """
        SELECT k.ID AS Klient_ID, k.Vorname, k.Nachname, 
        SUM(f.kilometer) AS gesamt_km
        FROM klient k 
        JOIN zeiteintrag z ON k.ID = z.Klient_ID 
        JOIN fahrt f ON z.ID = f.Zeiteintrag_ID 
        WHERE k.ID = %s AND MONTH(z.end_zeit) = %s AND YEAR(z.end_zeit) = %s
    """

    params = [klient_id, month, year]

    # Optional: Filtern nach Mitarbeiter-ID, wenn eine solche übergeben wird
    if mitarbeiter_id:
        query += " AND z.mitarbeiter_id = %s"
        params.append(mitarbeiter_id)

    query += " GROUP BY k.ID ORDER BY k.ID"

    cursor.execute(query, params)
    return cursor.fetchall()


# /FMOF030/
# /FMOF050/
# /FGF010/
def client_dropdown():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, vorname, nachname FROM klient")
    items = []
    for (ID, vorname, nachname) in cursor.fetchall():
        items.append({'id': ID, 'vorname': vorname, 'nachname': nachname})
    connection.close()
    return items


def create_klient(vorname, nachname, geburtsdatum, telefonnummer, sachbearbeiter_id,
                  adresse, kontingent_hk, kontingent_fk, fallverantwortung_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO klient (vorname, nachname, geburtsdatum, telefonnummer, sachbearbeiter_ID, "
                   "adresse, kontingent_HK, kontingent_FK, fallverantwortung_ID) VALUES "
                   "(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                   (vorname, nachname, geburtsdatum, telefonnummer, sachbearbeiter_id,
                    adresse, kontingent_hk, kontingent_fk, fallverantwortung_id))
    connection.commit()
    cursor.close()


def validate_client(vorname, nachname, geburtsdatum):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM klient WHERE vorname = %s AND nachname = %s AND geburtsdatum = %s",
                   (vorname, nachname, geburtsdatum,))
    result = cursor.fetchone()
    if result:
        return True
    return False


def get_klient_data(client_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM klient WHERE ID = %s", (client_id,))
    result = cursor.fetchall()
    return result


def edit_klient_fct(client_id, vorname, nachname, geburtsdatum, adresse, telefonnummer=None, sachbearbeiter_id=None,
                    kontingent_fk=None, kontingent_hk=None, fallverantwortung_id=None):
    connection = get_database_connection()
    cursor = connection.cursor()

    query = "UPDATE klient SET "
    parameters = []

    # Diese Felder sind immer vorhanden
    query += "vorname = %s, nachname = %s, geburtsdatum = %s, adresse = %s, "
    parameters += [vorname, nachname, geburtsdatum, adresse]

    telefonnummer = None if telefonnummer == '' else telefonnummer
    sachbearbeiter_id = None if sachbearbeiter_id == '' else sachbearbeiter_id
    kontingent_fk = None if kontingent_fk == '' else kontingent_fk
    kontingent_hk = None if kontingent_hk == '' else kontingent_hk
    fallverantwortung_id = None if fallverantwortung_id == '' else fallverantwortung_id

    # Optionale Felder, können None sein
    if telefonnummer is not None:
        query += "telefonnummer = %s, "
        parameters.append(telefonnummer)
    else:
        query += "telefonnummer = NULL, "

    if sachbearbeiter_id is not None:
        query += "sachbearbeiter_id = %s, "
        parameters.append(sachbearbeiter_id)
    else:
        query += "sachbearbeiter_id = NULL, "

    if kontingent_fk is not None:
        query += "kontingent_fk = %s, "
        parameters.append(kontingent_fk)
    else:
        query += "kontingent_fk = NULL, "

    if kontingent_hk is not None:
        query += "kontingent_hk = %s, "
        parameters.append(kontingent_hk)
    else:
        query += "kontingent_hk = NULL, "

    if fallverantwortung_id is not None:
        query += "fallverantwortung_id = %s, "
        parameters.append(fallverantwortung_id)
    else:
        query += "fallverantwortung_id = NULL, "

    # Letztes Komma und Leerzeichen entfernen
    query = query[:-2]

    # WHERE-Klausel hinzufügen
    query += " WHERE id = %s"
    parameters.append(client_id)

    cursor.execute(query, parameters)
    connection.commit()
    cursor.close()
    connection.close()


def edit_klient(klient_id, vorname, nachname, geburtsdatum, telefonnummer, sachbearbeiter_id, adresse, kontingent_hk,
                kontingent_fk, fallverantwortung_id):
    # Stellen Sie hier die Verbindung zur Datenbank her
    connection = get_database_connection()
    cursor = connection.cursor()

    # Bereite die Werte für die SQL-Anweisung vor
    sachbearbeiter_value = "NULL" if sachbearbeiter_id in [None, ''] else "%s"
    fallverantwortung_value = "NULL" if fallverantwortung_id in [None, ''] else "%s"

    # SQL-Update-Anweisung mit bedingten Platzhaltern
    update_query = f"""
           UPDATE klient 
           SET vorname = %s, 
               nachname = %s, 
               geburtsdatum = %s, 
               telefonnummer = %s, 
               sachbearbeiter_ID = {sachbearbeiter_value}, 
               adresse = %s, 
               kontingent_HK = %s, 
               kontingent_FK = %s, 
               fallverantwortung_ID = {fallverantwortung_value} 
           WHERE ID = %s
       """

    # Erstelle eine Liste der Parameter und schließe None-Werte aus
    params = [vorname, nachname, geburtsdatum, telefonnummer, adresse, kontingent_hk, kontingent_fk, klient_id]
    if sachbearbeiter_value != "NULL":
        params.insert(4, sachbearbeiter_id)
    if fallverantwortung_value != "NULL":
        params.insert(-2, fallverantwortung_id)

    cursor.execute(update_query, tuple(params))
    connection.commit()

    cursor.close()
    connection.close()


def get_report_klient(date_from, date_to, client_id=None, mitarbeiter_id=None):
    connection = get_database_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            klient.id, 
            klient.nachname,
            klient.vorname,
            TIME_FORMAT(SEC_TO_TIME(SUM(TIMESTAMPDIFF(MINUTE, zeiteintrag.start_zeit, zeiteintrag.end_zeit) * 60)), '%H:%i') AS geleistete_stunden,
            SUM(fahrt.kilometer) AS gefahrene_kilometer,
            SUM(CASE WHEN fahrt.abrechenbar THEN fahrt.kilometer ELSE 0 END) AS abrechenbare_km,
            SUM(CASE WHEN fahrt.abrechenbar THEN 0 ELSE fahrt.kilometer END) AS nicht_abrechenbare_km,
            SUM(CASE WHEN zeiteintrag.absage THEN 1 ELSE 0 END) AS Absage
        FROM
            zeiteintrag
        INNER JOIN klient ON zeiteintrag.klient_ID = klient.id
        LEFT JOIN fahrt ON zeiteintrag.id = fahrt.zeiteintrag_id
        WHERE
            zeiteintrag.start_zeit >= %s AND
            zeiteintrag.start_zeit < %s
    """
    params = [date_from, date_to]

    if client_id is not None:
        query += " AND klient.ID = %s"
        params.append(client_id)

    elif mitarbeiter_id is not None:
        query += " AND zeiteintrag.mitarbeiter_ID = %s"
        params.append(mitarbeiter_id)

    query += " GROUP BY klient.id ORDER BY klient.id ASC"
    cursor.execute(query, tuple(params))
    return cursor.fetchall()


def sum_hours_klient_zeitspanne(start_date, end_date):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT k.ID AS Klient_ID, z.mitarbeiter_ID AS Mitarbeiter_ID, k.Vorname, k.Nachname, 
        TIME_FORMAT(SEC_TO_TIME(SUM(TIMESTAMPDIFF(MINUTE, z.start_zeit, z.end_zeit) * 60)), '%H:%i') AS anzahl_Stunden 
        FROM klient k 
        JOIN zeiteintrag z ON k.ID = z.Klient_ID 
        WHERE z.end_zeit BETWEEN %s AND %s 
        GROUP BY k.ID , z.mitarbeiter_ID
        ORDER BY k.ID
    """, (start_date, end_date))

    return cursor.fetchall()


def sum_absage_klient(start_date, end_date):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT k.ID AS Klient_ID, z.mitarbeiter_ID AS Mitarbeiter_ID, k.Vorname, k.Nachname, COUNT(z.ID) AS anzahl_Absagen 
        FROM klient k 
        JOIN zeiteintrag z ON k.ID = z.Klient_ID 
        WHERE z.end_zeit BETWEEN %s AND %s AND z.absage = 1 
        GROUP BY k.ID , z.mitarbeiter_ID
        ORDER BY k.ID
    """, (start_date, end_date))
    return cursor.fetchall()


def sum_km_klient(start_date, end_date):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT k.ID AS Klient_ID, z.mitarbeiter_ID AS Mitarbeiter_ID, k.Vorname, k.Nachname, 
        SUM(f.kilometer) AS gesamt_km, SUM(IF(f.abrechenbar = 1, f.kilometer, 0)) 
        AS abrechenbare_km, SUM(IF(f.abrechenbar = 0, f.kilometer, 0)) AS nichtabrechenbare_km 
        FROM klient k 
        JOIN zeiteintrag z ON k.ID = z.Klient_ID 
        JOIN fahrt f ON z.ID = f.Zeiteintrag_ID 
        WHERE z.end_zeit BETWEEN %s AND %s
        GROUP BY k.ID , z.mitarbeiter_ID
        ORDER BY k.ID
    """, (start_date, end_date))
    return cursor.fetchall()


def get_client_table_client_sb(client_id, person_id, month, year):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT 
            z.ID as id, 
            DATE_FORMAT(z.end_zeit, '%d.%m.%Y') as Datum, 
            z.beschreibung as Beschreibung, 
            SUM(f.kilometer) as Kilometer, 
            DATE_FORMAT(z.start_zeit, '%H:%i') AS Anfang,
            DATE_FORMAT(z.end_zeit, '%H:%i') AS Ende,
            CONCAT(p.vorname, ' ', p.nachname) as Mitarbeiter, 
            CASE WHEN z.fachkraft = 1 THEN 'Fachkraft' ELSE 'Hilfskraft' END as Fachkraft_Hilfskraft, 
            # IFNULL(CONVERT(IFNULL(CONVERT(z.unterschrift_klient USING utf8mb4), '') USING latin1), '') 
            z.unterschrift_Klient as Unterschrift_Klient, 
            # IFNULL(CONVERT(IFNULL(CONVERT(z.unterschrift_mitarbeiter USING utf8mb4), '') USING latin1), '') 
            z.unterschrift_Mitarbeiter as Unterschrift_Mitarbeiter 
        FROM 
            klient k 
            LEFT JOIN zeiteintrag z ON k.ID = z.klient_id 
            LEFT JOIN fahrt f ON z.ID = f.zeiteintrag_id 
            LEFT JOIN person p ON z.mitarbeiter_id = p.ID 
        WHERE 
            k.ID = %s AND 
            k.sachbearbeiter_ID = %s AND 
            MONTH(z.start_zeit) = %s AND 
            YEAR(z.start_zeit) = %s
        GROUP BY 
            z.ID, 
            p.ID
    """, (client_id, person_id, month, year))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


def get_client_name(client_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT vorname, nachname FROM klient WHERE ID = %s", (client_id,))
    client_name = cursor.fetchone()
    cursor.close()
    return client_name
