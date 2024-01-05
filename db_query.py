import hashlib
import json
from flask import session
from database_connection import get_database_connection
from passlib.hash import sha1_crypt


# /FS010/
def get_current_person(person_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM person WHERE ID = %s", (person_id,))
    old_state = cursor.fetchone()
    cursor.close()
    connection.close()
    if old_state is None:
        return None
    return old_state


# /FS010/
def get_current_client(client_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM klient WHERE ID = %s", (client_id,))
    old_state = cursor.fetchone()
    cursor.close()
    connection.close()
    if old_state is None:
        return None
    return old_state


# /FS010/
def get_new_person(person_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM person WHERE ID = %s", (person_id,))
    new_state = cursor.fetchone()
    cursor.close()
    connection.close()
    if new_state is None:
        return None
    return new_state


# /FS010/
def get_new_client(client_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM klient WHERE ID = %s", (client_id,))
    new_state = cursor.fetchone()
    cursor.close()
    connection.close()
    if new_state is None:
        return None
    return new_state


# /FS010/
def save_change_log(person_id, table_type, old_state, new_state):
    connection = get_database_connection()
    cursor = connection.cursor()
    # Den alten Zustand als JSON-String speichern
    old_state_json = json.dumps(old_state)
    # Den neuen Zustand als JSON-String speichern
    new_state_json = json.dumps(new_state)
    # Die Änderungsprotokolle in der Datenbank speichern
    cursor.execute(
        "INSERT INTO protokoll (person_id, eintragungsart, eintrag_vorher, eintrag_nachher) VALUES (%s, %s, %s, %s)",
        (person_id, table_type, old_state_json, new_state_json))

    connection.commit()
    cursor.close()
    connection.close()


# /FS030/
# /FMOF010/
# /FMOF030/
# /FSK010/
def check_for_overlapping_zeiteintrag(zeiteintrag_id, klient_id, start_time, end_time):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id FROM zeiteintrag WHERE id != %s AND klient_id = %s "
        "AND ((start_zeit >= %s AND start_zeit < %s) "
        "OR (end_zeit > %s AND end_zeit <= %s) "
        "OR (start_zeit <= %s AND end_zeit >= %s))",
        (zeiteintrag_id, klient_id, start_time, end_time, start_time, end_time, start_time, end_time))
    ids = [id[0] for id in cursor.fetchall()]
    cursor.close()
    connection.close()
    return ids


# /FNAN010/
def validate_login(email, password):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT passwort FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()  # erstes Ergebnis wird aufgerufen
    if result:
        hashed_password = result[0]
        if hashlib.sha1(password.encode()).hexdigest() == hashed_password:
            return True
    return False


# /FNAN010/
# /FNAN020/
def check_account_locked(email):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT sperre FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()
    if result:
        if result[0] == 1:
            return True
    return False


# /FNAN020/
def set_password_mail(email, new_password):
    hashed_password = hashlib.sha1(new_password.encode()).hexdigest()
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE person SET passwort = %s WHERE email = %s",
                   (hashed_password, email,))
    connection.commit()
    cursor.close()
    connection.close()


# /FNAN020/
def validate_email(email):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()
    if result:
        return True
    return False


# /FAN010/
# /FAN020/
# /FAN030/
# /FAN040/
def get_role_by_id(person_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT rolle FROM person WHERE ID = %s", (person_id,))
    result = cursor.fetchone()  # erstes Ergebnis wird aufgerufen
    cursor.close()
    return result[0] if result else None


# /FAN030/
def account_table_mitarbeiter(monat, year, person_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT person.ID, person.nachname, person.vorname, "
        "SUM(TIMESTAMPDIFF(MINUTE , zeiteintrag.start_zeit, zeiteintrag.end_zeit)) AS geleistete_stunden "
        "FROM person JOIN zeiteintrag ON person.ID = zeiteintrag.mitarbeiter_ID "
        "WHERE EXTRACT(MONTH FROM zeiteintrag.end_zeit) = %s "
        "AND EXTRACT(YEAR FROM zeiteintrag.end_zeit) = %s "
        "AND person.ID = %s GROUP BY person.ID ", (monat, year, person_id))
    time_table_mitarbeiter = cursor.fetchall()

    cursor.execute(
        "SELECT person.ID, person.nachname, person.vorname, "
        "SUM(fahrt.kilometer) AS gefahrene_kilometer "
        "FROM person JOIN zeiteintrag ON person.ID = zeiteintrag.mitarbeiter_ID "
        "JOIN fahrt ON zeiteintrag.ID = fahrt.zeiteintrag_ID "
        "WHERE EXTRACT(MONTH FROM zeiteintrag.end_zeit) = %s "
        "AND EXTRACT(YEAR FROM zeiteintrag.end_zeit) = %s "
        "AND person.ID = %s GROUP BY person.ID", (monat, year, person_id))
    distance_table_mitarbeiter = cursor.fetchall()
    # Zusammenfügen der Tabellen
    report_table = []
    for time_spalte, distance_spalte in zip(time_table_mitarbeiter, distance_table_mitarbeiter):
        geleistete_stunden = int(time_spalte[3])
        stunden = geleistete_stunden // 60  # Ganzzahlige Division für Stunden
        minuten = geleistete_stunden % 60  # Rest für Minuten
        if time_spalte[0] == distance_spalte[0]:  # IDs müssen übereinstimmen

            report_table.append(
                (
                    time_spalte[0],  # ID
                    time_spalte[1],  # vorname
                    time_spalte[2],  # nachname
                    f"{stunden}h {minuten}min",  # geleistete_stunden
                    distance_spalte[3],  # gefahrene_kilometer
                )
            )
    return report_table


# /FAN030/
def account_table(monat, year):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT person.ID, person.nachname, person.vorname, "
        "SUM(TIMESTAMPDIFF(MINUTE, zeiteintrag.start_zeit, zeiteintrag.end_zeit)) AS geleistete_stunden "
        "FROM person JOIN zeiteintrag ON person.ID = zeiteintrag.mitarbeiter_ID "
        "WHERE EXTRACT(MONTH FROM zeiteintrag.end_zeit) = %s "
        "AND EXTRACT(YEAR FROM zeiteintrag.end_zeit) = %s "
        "GROUP BY person.ID", (monat, year,))
    time_table = cursor.fetchall()

    cursor.execute(
        "SELECT person.ID, person.nachname, person.vorname, "
        "SUM(fahrt.kilometer) AS gefahrene_kilometer "
        "FROM person JOIN zeiteintrag ON person.ID = zeiteintrag.mitarbeiter_ID "
        "JOIN fahrt ON zeiteintrag.ID = fahrt.zeiteintrag_ID "
        "WHERE EXTRACT(MONTH FROM zeiteintrag.end_zeit) = %s "
        "AND EXTRACT(YEAR FROM zeiteintrag.end_zeit) = %s "
        "GROUP BY person.ID", (monat, year,))
    distance_table = cursor.fetchall()
    # Zusammenfügen der Tabellen
    report_table = []
    for time_spalte, distance_spalte in zip(time_table, distance_table):
        geleistete_stunden = int(time_spalte[3])
        stunden = geleistete_stunden // 60  # Ganzzahlige Division für Stunden
        minuten = geleistete_stunden % 60  # Rest für Minuten
        if time_spalte[0] == distance_spalte[0]:  # IDs müssen übereinstimmen
            report_table.append(
                (
                    time_spalte[0],  # ID
                    time_spalte[1],  # vorname
                    time_spalte[2],  # nachname
                    f"{stunden}:{minuten}",  # geleistete_stunden
                    distance_spalte[3],  # gefahrene_kilometer
                )
            )
    return report_table


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


# /FAN040/
def get_client_table_sb(person_id, month, year):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT k.ID, k.nachname, k.vorname,
            k.kontingent_FK, k.kontingent_HK,
            k.kontingent_FK - SUM(CASE WHEN z.fachkraft = 1 THEN TIMESTAMPDIFF(HOUR, z.start_zeit, z.end_zeit)
            ELSE 0 END) as fachkraftsaldo,
            k.kontingent_HK - SUM(CASE WHEN z.fachkraft = 0 THEN TIMESTAMPDIFF(HOUR, z.start_zeit, z.end_zeit)
            ELSE 0 END) as hilfskraftsaldo,
            CONCAT(p.vorname, ' ', p.nachname) AS Fallverantwortung
        FROM klient k
        LEFT JOIN zeiteintrag z ON k.ID = z.klient_id
        LEFT JOIN person p ON k.fallverantwortung_ID = p.ID
        WHERE k.fallverantwortung_ID = %s AND MONTH(z.start_zeit) = %s AND YEAR(z.start_zeit) = %s
        GROUP BY k.ID, p.nachname, p.vorname
    """, (person_id, month, year))
    client_info = cursor.fetchone()
    cursor.close()
    return client_info


# /FAN040/
def get_client_table(month, year):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT k.ID, k.nachname, k.vorname,
            k.kontingent_FK, k.kontingent_HK,
            k.kontingent_FK - SUM(CASE WHEN z.fachkraft = 1 THEN TIMESTAMPDIFF(HOUR, z.start_zeit, z.end_zeit)
            ELSE 0 END) as fachkraftsaldo,
            k.kontingent_HK - SUM(CASE WHEN z.fachkraft = 0 THEN TIMESTAMPDIFF(HOUR, z.start_zeit, z.end_zeit)
            ELSE 0 END) as hilfskraftsaldo,
            CONCAT(p.vorname, ' ', p.nachname) AS Fallverantwortung
        FROM klient k
        LEFT JOIN zeiteintrag z ON k.ID = z.klient_id
        LEFT JOIN person p ON k.fallverantwortung_ID = p.ID
        WHERE MONTH(z.start_zeit) = %s AND YEAR(z.start_zeit) = %s
        GROUP BY k.ID, p.nachname, p.vorname
    """, (month, year))
    client_info = cursor.fetchall()
    cursor.close()
    return client_info


# /FAN060/
def validate_reset(person_id, password):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT passwort FROM person WHERE ID = %s", (person_id,))
    result = cursor.fetchone()  # erstes Ergebnis wird aufgerufen
    if result:
        hashed_password = result[0]
        if hashlib.sha1(password.encode()).hexdigest() == hashed_password:
            return True
    return False


# /FAN060/
def set_password_id(person_id, new_passwort):
    hashed_password = sha1_crypt.encrypt(new_passwort)
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE person SET passwort = %s WHERE ID = %s",
                   (hashed_password, person_id,))
    connection.commit()
    cursor.close()
    connection.close()


# /FAN060/
def set_password_required_true(email):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE person SET passwort_erzwingen = 1 WHERE email = %s", (email,))
    connection.commit()
    cursor.close()
    connection.close()


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
                   unterschrift_mitarbeiter, unterschrift_klient, start_time, end_time, session['user_id'],
                   klient_id, fachkraft, beschreibung, interne_notiz, absage)
    zeiteintrag_id = cursor.lastrowid
    connection.commit()
    cursor.close()
    connection.close()
    return zeiteintrag_id


# /FMOF030/
# /FMOF050/
def add_fahrt(kilometer, start_adresse, end_adresse, abrechenbar, zeiteintrag_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO fahrt (kilometer, start_adresse, end_adresse, abrechenbar, zeiteintrag_ID) "
                   "VALUES (%s, %s, %s, %s, %s)", kilometer, start_adresse, end_adresse, abrechenbar, zeiteintrag_id)
    connection.commit()
    cursor.close()
    connection.close()


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


# /FMOF030/
# /FMOF050/
# /FGF010/
def client_dropdown():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, nachname FROM klient")
    items = []
    for (ID, nachname) in cursor.fetchall():
        items.append({'id': ID, 'nachname': nachname})
    connection.close()
    return items


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
# /FV100/
def edit_zeiteintrag(zeiteintrag_id, start_time=None, end_time=None, unterschrift_mitarbeiter=None,
                     unterschrift_klient=None, klient_id=None, fachkraft=None,
                     beschreibung=None, interne_notiz=None, absage=None):
    connection = get_database_connection()
    cursor = connection.cursor()
    if unterschrift_mitarbeiter is not None and unterschrift_klient is not None:
        cursor.execute("UPDATE zeiteintrag SET start_zeit = %s, end_zeit = %s, unterschrift_Mitarbeiter = %s, "
                       "unterschrift_Klient = %s, klient_ID = %s, fachkraft = %s, "
                       "beschreibung = %s, interne_notiz = %s, absage = %s "
                       "WHERE ID = %s",
                       (start_time, end_time, unterschrift_mitarbeiter, unterschrift_klient, klient_id, fachkraft,
                        beschreibung, interne_notiz, absage, zeiteintrag_id))
    else:
        cursor.execute("UPDATE zeiteintrag SET start_zeit = %s, end_zeit = %s, unterschrift_Mitarbeiter = NULL, "
                       "unterschrift_Klient = NULL, klient_ID = %s, fachkraft = %s, "
                       "beschreibung = %s, interne_notiz = %s, absage = %s "
                       "WHERE ID = %s",
                       (start_time, end_time, unterschrift_mitarbeiter, unterschrift_klient, klient_id, fachkraft,
                        beschreibung, interne_notiz, absage, zeiteintrag_id))
    connection.commit()
    cursor.close()
    connection.close()


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
    cursor.execute("DELETE FROM fahrt WHERE id = %s", fahrt_id)
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


# /FV010/
def get_steuerbuero_table():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT ID, nachname, vorname, email FROM person WHERE rolle = 'Steuerbüro'")
    result = cursor.fetchall()
    return result


# /FV010/
def get_sachbearbeiter_table():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT ID, nachname, vorname, email FROM person WHERE rolle = 'Kostenträger'")
    result = cursor.fetchall()
    return result


# /FV020/
def rolle_dropdown():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, rolle FROM person")
    items = []
    for (ID, rolle) in cursor.fetchall():
        items.append({'id': ID, 'rolle': rolle})
    connection.close()
    return items


# /FV020/
def create_account_db(vorname, nachname, geburtsdatum, qualifikation, adresse, rolle, email,
                      telefonnummer, passwort, sperre, passwort_erzwingen):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO person (vorname, nachname, geburtsdatum, qualifikation, adresse, rolle, email, "
                   "telefonnummer, passwort, sperre, passwort_erzwingen) VALUES "
                   "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                   (vorname, nachname, geburtsdatum, qualifikation, adresse, rolle, email,
                    telefonnummer, passwort, sperre, passwort_erzwingen))
    connection.commit()
    cursor.close()


# /FV030/
def get_person_data(account_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM person WHERE ID = %s", (account_id,))
    result = cursor.fetchall()
    return result


# /FV040/
def edit_account(vorname, nachname, geburtsdatum, qualifikation, adresse, rolle, email,
                 telefonnummer, passwort, sperre, passwort_erzwingen, account_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE person SET vorname = %s, nachname = %s, geburtsdatum = %s, qualifikation = %s, "
                   "adresse = %s, rolle = %s, email = %s, telefonnummer = %s, passwort = %s, sperre = %s, "
                   "passwort_erzwingen = %s WHERE ID = %s",
                   (vorname, nachname, geburtsdatum, qualifikation, adresse, rolle, email,
                    telefonnummer, passwort, sperre, passwort_erzwingen, account_id))
    connection.commit()
    cursor.close()


# /FV050/
def edit_account_lock(person_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE person SET sperre = %s WHERE ID = %s", (True, person_id))
    connection.commit()
    cursor.close()


# /FV060/
def edit_account_unlock(person_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE person SET sperre = %s WHERE ID = %s", (False, person_id))
    connection.commit()
    cursor.close()


# /FV070/
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


# /FV070/
def validate_client(vorname, nachname, geburtsdatum):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM klient WHERE vorname = %s AND nachname = %s AND geburtsdatum = %s",
                   (vorname, nachname, geburtsdatum,))
    result = cursor.fetchone()
    if result:
        return True
    return False


# /FV080
def get_klient_data(client_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM klient WHERE ID = %s", (client_id,))
    result = cursor.fetchall()
    return result


# /FV080
def get_name_by_id(person_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT vorname, nachname FROM person WHERE ID = %s", (person_id,))
    result = cursor.fetchall()
    return result


# /FV090/
def edit_klient(person_id, klient_id, vorname, nachname, geburtsdatum, telefonnummer, sachbearbeiter_id, adresse,
                kontingent_hk, kontingent_fk, fallverantwortung_id):
    connection = get_database_connection()
    cursor = connection.cursor()

    # Überprüfen, ob die Person berechtigt ist, den Klienten zu bearbeiten
    cursor.execute("""
        SELECT 1
        FROM klient k join person p on p.ID = k.fallverantwortung_ID
        WHERE p.ID = %s AND k.fallverantwortung_ID = %s
    """, (person_id, fallverantwortung_id))
    is_fallverantwortung = bool(cursor.fetchone())

    cursor.execute("""
        SELECT 1
        FROM klient k join person p on k.sachbearbeiter_ID = p.ID
        WHERE k.sachbearbeiter_ID = %s AND p.ID = %s
    """, (sachbearbeiter_id, person_id))
    is_sachbearbeiter = bool(cursor.fetchone())

    if not is_fallverantwortung and not is_sachbearbeiter:
        raise Exception("Person hat keine Berechtigung, den Klienten zu bearbeiten")

    # Klienten bearbeiten
    cursor.execute("UPDATE klient SET vorname = %s, nachname = %s, geburtsdatum = %s, telefonnummer = %s, "
                   "sachbearbeiter_ID = %s, adresse = %s, kontingent_HK = %s, kontingent_FK = %s, "
                   "fallverantwortung_ID = %s WHERE ID = %s",
                   (vorname, nachname, geburtsdatum, telefonnummer, sachbearbeiter_id, adresse,
                    kontingent_hk, kontingent_fk, fallverantwortung_id, klient_id))
    connection.commit()


# /FV100/
# /FV110/
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


# /FV120/
def check_signatures(client_id, month, year):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
       SELECT * FROM zeiteintrag 
       WHERE Klient_ID = %s AND MONTH(end_zeit) = %s AND YEAR(end_zeit) = %s
   """, (client_id, month, year))
    results = cursor.fetchall()
    if not results:
        return False
    for result in results:
        if result["unterschrift_Klient"].is_null() or result["unterschrift_Mitarbeiter"].is_null():
            return False
    return True


# /FV120/
def book_zeiteintrag(client_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM buchung 
        WHERE Klient_ID = %s ORDER BY monat DESC LIMIT 1
    """, (client_id,))
    last_entry = cursor.fetchone()
    if not last_entry:
        return False
    start_month = last_entry["end_zeit"].month
    start_year = last_entry["end_zeit"].year
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
    for result in results:
        if result["fachkraft"]:
            fk_hours += result["end_zeit"].hour - result["start_zeit"].hour
        else:
            hk_hours += result["end_zeit"].hour - result["start_zeit"].hour
    saldo_fk = client["kontingent_fk"] - fk_hours
    saldo_hk = client["kontingent_hk"] - hk_hours
    cursor.execute("""
        INSERT INTO buchung (Klient_ID, monat, saldo_FK, saldo_HK)
        VALUES (%s, %s, %s, %s)
    """, (client_id, last_entry["end_zeit"], saldo_fk, saldo_hk))
    connection.commit()
    return True


# /FGF010/
def get_report_zeiteintrag(date_from, date_to):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            CONCAT(Mitarbeiter.vorname, ' ', Mitarbeiter.nachname) AS Mitarbeiter,
            CONCAT(Sachbearbeiter.vorname, ' ', Sachbearbeiter.nachname) AS Sachbearbeiter, 
            CONCAT(klient.vorname, ' ', klient.nachname) AS Klient,
            SUM(TIMESTAMPDIFF(HOUR, zeiteintrag.start_zeit, zeiteintrag.end_zeit)) AS geleistete_stunden,
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
        GROUP BY
            Mitarbeiter.id,
            Sachbearbeiter.id,
            klient.id
    """, (date_from, date_to))
    return cursor.fetchall()


# /FGF010/
def get_report_mitarbeiter(date_from, date_to):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
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
        GROUP BY Mitarbeiter.ID
    """, (date_from, date_to))
    return cursor.fetchone()


# /FGF010/
def get_report_klient(date_from, date_to):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            klient.id, 
            klient.nachname,
            klient.vorname,
            TIME_FORMAT(SEC_TO_TIME(SUM(TIMESTAMPDIFF(MINUTE, zeiteintrag.start_zeit, zeiteintrag.end_zeit) * 60)), '%H:%i') AS geleistete_stunden,
            SUM(fahrt.kilometer) AS gefahrene_kilometer,
            SUM(CASE WHEN fahrt.abrechenbar THEN fahrt.kilometer ELSE 0 END) AS abrechenbare_km,
            SUM(CASE WHEN fahrt.abrechenbar THEN 0 ELSE fahrt.kilometer END) AS nicht_abrechenbare_km,
            SUM(CASE WHEN zeiteintrag.Absage THEN 1 ELSE 0 END) AS Absage
        FROM
            zeiteintrag
        INNER JOIN klient ON zeiteintrag.mitarbeiter_id = klient.id
        LEFT JOIN fahrt ON zeiteintrag.id = fahrt.zeiteintrag_id
        WHERE
            zeiteintrag.start_zeit >= %s AND
            zeiteintrag.start_zeit < %s
        GROUP BY klient.ID
    """, (date_from, date_to))
    return cursor.fetchone()


# /FGF010/
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


# /FGF010/
def sum_hours_klient(month, year):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT k.ID AS Klient_ID, k.Vorname, k.Nachname, 
        TIME_FORMAT(SEC_TO_TIME(SUM(TIMESTAMPDIFF(MINUTE, z.start_zeit, z.end_zeit) * 60)), '%H:%i') AS anzahl_Stunden 
        FROM klient k 
        JOIN zeiteintrag z ON k.ID = z.Klient_ID 
        WHERE MONTH(z.end_zeit) = %s AND YEAR(z.end_zeit) = %s 
        GROUP BY k.ID 
        ORDER BY k.ID
    """, (month, year))
    return cursor.fetchall()


# /FGF010/
def sum_hours_klient_zeitspanne(start_date, end_date):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT k.ID AS Klient_ID, k.Vorname, k.Nachname, 
        TIME_FORMAT(SEC_TO_TIME(SUM(TIMESTAMPDIFF(MINUTE, z.start_zeit, z.end_zeit) * 60)), '%H:%i') AS anzahl_Stunden 
        FROM klient k 
        JOIN zeiteintrag z ON k.ID = z.Klient_ID 
        WHERE z.end_zeit BETWEEN %s AND %s 
        GROUP BY k.ID 
        ORDER BY k.ID
    """, (start_date, end_date))

    return cursor.fetchall()


# /FGF010/
def sum_hours_mitarbeiter_zeitspanne(start_date, end_date):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT p.ID AS Mitarbeiter_ID, p.Vorname, p.Nachname, 
        TIME_FORMAT(SEC_TO_TIME(SUM(TIMESTAMPDIFF(MINUTE, z.start_zeit, z.end_zeit) * 60)), '%H:%i') AS anzahl_Stunden 
        FROM person p 
        JOIN zeiteintrag z ON p.ID = z.Mitarbeiter_ID 
        WHERE z.end_zeit BETWEEN %s AND %s 
        GROUP BY p.ID 
        ORDER BY p.ID
    """, (start_date, end_date))
    return cursor.fetchall()


# /FGF010/
def sum_absage_klient(start_date, end_date):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT k.ID AS Klient_ID, k.Vorname, k.Nachname, COUNT(z.ID) AS anzahl_Absagen 
        FROM klient k 
        JOIN zeiteintrag z ON k.ID = z.Klient_ID 
        WHERE z.end_zeit BETWEEN %s AND %s AND z.absage = 1 
        GROUP BY k.ID 
        ORDER BY k.ID
    """, (start_date, end_date))
    return cursor.fetchall()


# /FGF010/
def sum_absage_mitarbeiter(start_date, end_date):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT p.ID AS Mitarbeiter_ID, p.Vorname, p.Nachname, COUNT(z.ID) AS anzahl_Absagen 
        FROM person p 
        JOIN zeiteintrag z ON p.ID = z.Mitarbeiter_ID 
        WHERE z.end_zeit BETWEEN %s AND %s AND z.absage = 1
        GROUP BY p.ID 
        ORDER BY p.ID
    """, (start_date, end_date))
    return cursor.fetchall()


# /FGF010/
def sum_km_klient(start_date, end_date):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT k.ID AS Klient_ID, k.Vorname, k.Nachname, 
        SUM(f.kilometer) AS gesamt_km, SUM(IF(f.abrechenbar = 1, f.kilometer, 0)) 
        AS abrechenbare_km, SUM(IF(f.abrechenbar = 0, f.kilometer, 0)) AS nichtabrechenbare_km 
        FROM klient k 
        JOIN zeiteintrag z ON k.ID = z.Klient_ID 
        JOIN fahrt f ON z.ID = f.Zeiteintrag_ID 
        WHERE z.end_zeit BETWEEN %s AND %s
        GROUP BY k.ID 
        ORDER BY k.ID
    """, (start_date, end_date))
    return cursor.fetchall()


# /FGF010/
def sum_km_mitarbeiter(start_date, end_date):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT p.ID AS Mitarbeiter_ID, p.Vorname, p.Nachname, 
        SUM(f.kilometer) AS gesamt_km, SUM(IF(f.abrechenbar = 1, f.kilometer, 0)) 
        AS abrechenbare_km, SUM(IF(f.abrechenbar = 0, f.kilometer, 0)) AS nichtabrechenbare_km 
        FROM person p 
        JOIN zeiteintrag z ON p.ID = z.Mitarbeiter_ID 
        JOIN fahrt f ON z.ID = f.Zeiteintrag_ID 
        WHERE z.end_zeit BETWEEN %s AND %s
        GROUP BY p.ID 
        ORDER BY p.ID
    """, (start_date, end_date))
    return cursor.fetchall()


# /FGF010/
def mitarbeiter_dropdown():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, nachname FROM person WHERE rolle LIKE '%%Mitarbeiter%%'")
    items = []
    for (ID, nachname) in cursor.fetchall():
        items.append({'id': ID, 'nachname': nachname})
    connection.close()
    return items


# /FGF010/
def kostentraeger_dropdown():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, nachname FROM person WHERE rolle LIKE '%%Kostenträger%%'")
    items = []
    for (ID, nachname) in cursor.fetchall():
        items.append({'id': ID, 'nachname': nachname})
    connection.close()
    return items


# /FGF020/
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


# /FGF020/
def person_dropdown():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, nachname FROM person")
    items = []
    for (ID, nachname) in cursor.fetchall():
        items.append({'id': ID, 'nachname': nachname})
    connection.close()
    return items


# /FGF030/
def get_last_buchung(client_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT DATE_FORMAT(monat, '%Y-%m') as Monat, id FROM buchung 
        WHERE klient_id = %s 
        ORDER BY monat DESC 
        LIMIT 1
    """, (client_id,))
    return cursor.fetchone()


# /FGF030/
def delete_buchung(buchung_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM buchung WHERE id = %s", (buchung_id,))
    connection.commit()


# /FSK010/
def get_client_table_client_sb(person_id, month, year, client_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT 
            z.ID as id, 
            DATE(z.end_zeit) as Datum, 
            z.beschreibung as Beschreibung, 
            SUM(f.kilometer) as Kilometer, 
            TIME(z.start_zeit) as Anfang, 
            TIME(z.end_zeit) as Ende, 
            CONCAT(p.vorname, ' ', p.nachname) as Mitarbeiter, 
            CASE WHEN z.fachkraft = 1 THEN 'Fachkraft' ELSE 'Hilfskraft' END as Fachkraft_Hilfskraft, 
            IFNULL(CONVERT(IFNULL(CONVERT(z.unterschrift_klient USING utf8mb4), '') USING latin1), '') 
            as Unterschrift_Klient, 
            IFNULL(CONVERT(IFNULL(CONVERT(z.unterschrift_mitarbeiter USING utf8mb4), '') USING latin1), '') 
            as Unterschrift_Mitarbeiter 
        FROM 
            klient k 
            LEFT JOIN zeiteintrag z ON k.ID = z.klient_id 
            LEFT JOIN fahrt f ON z.ID = f.zeiteintrag_id 
            LEFT JOIN person p ON z.mitarbeiter_id = p.ID 
        WHERE 
            k.ID = %s AND 
            k.fallverantwortung_ID = %s AND 
            MONTH(z.start_zeit) = %s AND 
            YEAR(z.start_zeit) = %s
        GROUP BY 
            z.ID, 
            p.ID
    """, (client_id, person_id, month, year))
    client_table_data = cursor.fetchall()
    cursor.close()
    return client_table_data


# Folgende Methoden sind nicht Teil des Pflichtenhefts, sind aber evtl. nützlich!


# Methode, die die Rolle basierend auf der E-Mail aus der Datenbank abruft.
# Wenn ein Ergebnis gefunden wird, wird es als Rolle (str) zurückgegeben. Andernfalls wird None zurückgegeben.
def get_role_by_email(email):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT rolle FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()  # erstes Ergebnis wird aufgerufen
    cursor.close()
    return result[0] if result else None


# Methode gibt Vornamen zurück, wenn er in der Datenbank gefunden wird. Andernfalls gibt sie None zurück.
def get_firstname_by_email(email):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT vorname FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()  # erstes Ergebnis wird aufgerufen
    if result:
        return result[0]
    else:
        return None


# Methode gibt Nachnamen zurück, wenn er in der Datenbank gefunden wird. Andernfalls gibt sie None zurück.
def get_lastname_by_email(email):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT nachname FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()  # erstes Ergebnis wird aufgerufen
    if result:
        return result[0]
    else:
        return None


# Methode übergibt die ID der Person mit übergebener E-Mail
def get_person_id_by_email(email):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()  # erstes Ergebnis wird aufgerufen
    if result:
        return result[0]
    else:
        return None


def get_client_name(client_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT vorname, nachname FROM klient WHERE ID = %s", (client_id,))
    client_name = cursor.fetchone()
    cursor.close()
    return client_name


def get_sachbearbeiter_name(client_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT sachbearbeiter_id FROM klient WHERE ID = %s", (client_id,))
    sachbearbeiter_id = cursor.fetchone()
    if sachbearbeiter_id is not None:
        # Get Vorname and Nachname from Account table
        cursor.execute("SELECT vorname, nachname FROM person WHERE ID = %s", (sachbearbeiter_id[0],))
        sachbearbeiter_name = cursor.fetchone()
        return sachbearbeiter_name
    else:
        return None


def get_fallverantwortung_id(client_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT fallverantwortung_id FROM klient WHERE ID = %s", (client_id,))
    fallverantwortung_id = cursor.fetchone()

    if fallverantwortung_id is not None:
        return fallverantwortung_id[0]
    else:
        return None


def check_month_booked(datum, client_id):
    date_month = datum.strftime('%m')
    date_year = datum.strftime('%Y')
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM buchung WHERE EXTRACT(MONTH FROM monat) = %s AND EXTRACT(YEAR FROM monat) = %s "
                   "AND klient_ID = %s",
                   (date_month, date_year, client_id,))
    result = cursor.fetchone()
    if result:
        return True
    return False


# Gibt alle IDs der Zeiteinträge der übergebenen Person ID aus
def get_zeiteintrag_id(person_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM zeiteintrag WHERE mitarbeiter_ID = %s", (person_id,))
    result = cursor.fetchall()
    return result


# Ein Zeiteintrag wird zurückgegeben. Funktion gibt Dictionary zurück,
# bei dem jeder Schlüssel eine Zeiteintrag-ID ist und jeder Wert ein weiteres Dictionary ist,
# das die Zeiteintrag- und Fahrteninformationen enthält.
# list(zeiteintrag_fahrten.values()) zurückgeben dann erhält man das Ergebnis als Liste
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


def fahrt_id_existing(fahrt_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM fahrt WHERE id = %s",
                   (fahrt_id,))
    result = cursor.fetchone()
    if result:
        return True
    return False


def is_password_required(email):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT passwort_erzwingen FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result is None:
        return False
    return result[0] == 1


def check_person_locked(person_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT sperre FROM person WHERE ID = %s", (person_id,))
    result = cursor.fetchone()
    if result:
        if result[0] == 1:
            return True
    return False
