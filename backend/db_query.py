import hashlib
from flask import session
from database_connection import get_database_connection
from passlib.hash import sha1_crypt


# /FS030/
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
def set_password_mail(email, new_passwort):
    hashed_password = sha1_crypt.encrypt(new_passwort)
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
def account_table_mitarbeiter(monat, person_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT person.ID, person.nachname, person.vorname, "
        "SUM(TIMESTAMPDIFF(HOUR, zeiteintrag.start_zeit, zeiteintrag.end_zeit)) AS geleistete_stunden "
        "FROM person JOIN zeiteintrag ON person.ID = zeiteintrag.mitarbeiter_ID "
        "WHERE EXTRACT(MONTH FROM zeiteintrag.end_zeit) = %s AND person.ID = %s GROUP BY person.ID", (monat, person_id))
    time_table_mitarbeiter = cursor.fetchall()

    cursor.execute(
        "SELECT person.ID, person.nachname, person.vorname, "
        "SUM(fahrt.kilometer) AS gefahrene_kilometer "
        "FROM person JOIN zeiteintrag ON person.ID = zeiteintrag.mitarbeiter_ID "
        "JOIN fahrt ON zeiteintrag.ID = fahrt.zeiteintrag_ID "
        "WHERE EXTRACT(MONTH FROM zeiteintrag.end_zeit) = %s AND person.ID = %s GROUP BY person.ID", (monat, person_id))
    distance_table_mitarbeiter = cursor.fetchall()
    # Zusammenfügen der Tabellen
    report_table = []
    for time_spalte, distance_spalte in zip(time_table_mitarbeiter, distance_table_mitarbeiter):
        if time_spalte[0] == distance_spalte[0]:  # IDs müssen übereinstimmen
            report_table.append(
                (
                    time_spalte[0],  # ID
                    time_spalte[1],  # vorname
                    time_spalte[2],  # nachname
                    time_spalte[3],  # geleistete_stunden
                    distance_spalte[4],  # gefahrene_kilometer
                )
            )
    return report_table


# /FAN030/
def account_table(monat):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT person.ID, person.nachname, person.vorname, "
        "SUM(TIMESTAMPDIFF(HOUR, zeiteintrag.start_zeit, zeiteintrag.end_zeit)) AS geleistete_stunden "
        "FROM person JOIN zeiteintrag ON person.ID = zeiteintrag.mitarbeiter_ID "
        "WHERE EXTRACT(MONTH FROM zeiteintrag.end_zeit) = %s GROUP BY person.ID", (monat,))
    time_table = cursor.fetchall()

    cursor.execute(
        "SELECT person.ID, person.nachname, person.vorname, "
        "SUM(fahrt.kilometer) AS gefahrene_kilometer "
        "FROM person JOIN zeiteintrag ON person.ID = zeiteintrag.mitarbeiter_ID "
        "JOIN fahrt ON zeiteintrag.ID = fahrt.zeiteintrag_ID "
        "WHERE EXTRACT(MONTH FROM zeiteintrag.end_zeit) = %s GROUP BY person.ID", (monat,))
    distance_table = cursor.fetchall()
    # Zusammenfügen der Tabellen
    report_table = []
    for time_spalte, distance_spalte in zip(time_table, distance_table):
        if time_spalte[0] == distance_spalte[0]:  # IDs müssen übereinstimmen
            report_table.append(
                (
                    time_spalte[0],  # ID
                    time_spalte[1],  # vorname
                    time_spalte[2],  # nachname
                    time_spalte[3],  # geleistete_stunden
                    distance_spalte[4],  # gefahrene_kilometer
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


# Erzeugt einen neuen Eintrag (Account) in der Person-Tabelle
def create_account(vorname, nachname, geburtsdatum, qualifikation, adresse, rolle, email,
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


# Account mit übergebenen ID wird mit übergebenen Parameter bearbeitet
def edit_account(vorname, nachname, geburtsdatum, qualifikation, adresse, rolle, email,
                 telefonnummer, passwort, sperre, passwort_erzwingen):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE person SET vorname = %s, nachname = %s, geburtsdatum = %s, qualifikation = %s, "
                   "adresse = %s, rolle = %s, email = %s, telefonnummer = %s, passwort = %s, sperre = %s, "
                   "passwort_erzwingen = %s WHERE ID = %s",
                   (vorname, nachname, geburtsdatum, qualifikation, adresse, rolle, email,
                    telefonnummer, passwort, sperre, passwort_erzwingen))
    connection.commit()
    cursor.close()


def get_person_data(account_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM person WHERE ID = %s", (account_id,))
    result = cursor.fetchall()
    return result


# Account sperren
def edit_account_lock(person_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE person SET sperre = %s WHERE ID = %s", (True, person_id))
    connection.commit()
    cursor.close()


# Account entsperren
def edit_account_unlock(person_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE person SET sperre = %s WHERE ID = %s", (False, person_id))
    connection.commit()
    cursor.close()


def mitarbeiter_dropdown():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, nachname FROM person WHERE rolle LIKE '%%Mitarbeiter%%'")
    items = []
    for (ID, nachname) in cursor.fetchall():
        items.append({'id': ID, 'nachname': nachname})
    connection.close()
    return items


def rolle_dropdown():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, rolle FROM person")
    items = []
    for (ID, rolle) in cursor.fetchall():
        items.append({'id': ID, 'rolle': rolle})
    connection.close()
    return items


# Erzeugt einen neuen Eintrag in der Klient-Tabelle
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


# Klient mit übergebenen ID wird mit übergebenen Parameter bearbeitet
def edit_klient(client_id, vorname, nachname, geburtsdatum, telefonnummer, sachbearbeiter_id, adresse,
                kontingent_hk, kontingent_fk, fallverantwortung_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE klient SET vorname = %s, nachname = %s, geburtsdatum = %s, telefonnummer = %s, "
                   "sachbearbeiter_ID = %s, adresse = %s, kontingent_HK = %s, kontingent_FK = %s, "
                   "fallverantwortung_ID = %s WHERE ID = %s",
                   (vorname, nachname, geburtsdatum, telefonnummer, sachbearbeiter_id, adresse,
                    kontingent_hk, kontingent_fk, fallverantwortung_id, client_id))
    connection.commit()
    cursor.close()


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


# Prüft, ob schon ein Client mit dem Namen und Geburtsdatum existiert
def validate_client(vorname, nachname, geburtsdatum):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM klient WHERE vorname = %s AND nachname = %s AND geburtsdatum = %s",
                   (vorname, nachname, geburtsdatum,))
    result = cursor.fetchone()
    if result:
        return True
    return False


# returned json Vorschläge für eingabefeld
def client_dropdown():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, nachname FROM klient")
    items = []
    for (ID, nachname) in cursor.fetchall():
        items.append({'id': ID, 'nachname': nachname})
    connection.close()
    return items


# Gibt alle IDs der Zeiteinträge der übergebenen Person ID aus
def get_zeiteintrag_id(person_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM zeiteintrag WHERE mitarbeiter_ID = %s", (person_id,))
    result = cursor.fetchall()
    return result


# Erstellt einen neuen Zeiteintrag
def add_zeiteintrag(unterschrift_mitarbeiter, unterschrift_klient, start_time, end_time,
                    klient_id, beschreibung, interne_notiz):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO zeiteintrag (unterschrift_Mitarbeiter, unterschrift_Klient, start_zeit, end_zeit, "
                   "mitarbeiter_ID, klient_ID, beschreibung, interne_notiz, überschneidung, absage) "
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                   unterschrift_mitarbeiter, unterschrift_klient, start_time, end_time, session['user_id'],
                   klient_id, beschreibung, interne_notiz, False, False)
    zeiteintrag_id = cursor.lastrowid
    connection.commit()
    cursor.close()
    connection.close()
    return zeiteintrag_id


# Stunden werden im Zeiteintrag geändert mit Eingabe der Start- und Endzeit. Wenn keine Unterschriften übergeben
# werden, werden die Unterschriften gelöscht
def edit_zeiteintrag(zeiteintrag_id, start_time=None, end_time=None, unterschrift_mitarbeiter=None,
                     unterschrift_klient=None, klient_id=None,
                     beschreibung=None, interne_notiz=None, absage=None):
    connection = get_database_connection()
    cursor = connection.cursor()
    if unterschrift_mitarbeiter is not None and unterschrift_klient is not None:
        cursor.execute("UPDATE zeiteintrag SET start_zeit = %s, end_zeit = %s, unterschrift_Mitarbeiter = %s, "
                       "unterschrift_Klient = %s, klient_ID = %s, beschreibung = %s, interne_notiz = %s, absage = %s "
                       "WHERE ID = %s",
                       (start_time, end_time, unterschrift_mitarbeiter, unterschrift_klient, klient_id, beschreibung,
                        interne_notiz, absage, zeiteintrag_id))
    else:
        cursor.execute("UPDATE zeiteintrag SET start_zeit = %s, end_zeit = %s, unterschrift_Mitarbeiter = NULL, "
                       "unterschrift_Klient = NULL, klient_ID = %s, beschreibung = %s, interne_notiz = %s, absage = %s "
                       "WHERE ID = %s",
                       (start_time, end_time, unterschrift_mitarbeiter, unterschrift_klient, klient_id, beschreibung,
                        interne_notiz, absage, zeiteintrag_id))
    connection.commit()
    cursor.close()
    connection.close()


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


# Zeiteintrag wird gelöscht
def delete_zeiteintrag(zeiteintrag_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM fahrt WHERE zeiteintrag_ID = %s", (zeiteintrag_id,))
    cursor.execute("DELETE FROM zeiteintrag WHERE id = %s", (zeiteintrag_id,))
    connection.commit()
    cursor.close()
    connection.close()


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
            CONCAT(p.vorname, ' ', p.nachname) AS Mitarbeiter,
            z.überschneidung AS Überschneidung,
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
            CONCAT(p.vorname, ' ', p.nachname) AS Mitarbeiter,
            z.überschneidung AS Überschneidung,
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


# fügt eine Fahrt hinzu
def add_fahrt(kilometer, start_adresse, end_adresse, abrechenbar, zeiteintrag_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO fahrt (kilometer, start_adresse, end_adresse, abrechenbar, zeiteintrag_ID) "
                   "VALUES (%s, %s, %s, %s, %s)", kilometer, start_adresse, end_adresse, abrechenbar, zeiteintrag_id)
    connection.commit()
    cursor.close()
    connection.close()


def edit_fahrt(id, kilometer, abrechenbar, zeiteintrag_id, start_adresse=None, end_adresse=None):
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
    parameters.append(id)

    cursor.execute(query, parameters)
    connection.commit()
    cursor.close()
    connection.close()


def delete_fahrt(fahrt_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM fahrt WHERE id = %s", fahrt_id)
    connection.commit()
    cursor.close()
    connection.close()

