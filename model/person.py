import datetime
import hashlib
from passlib.handlers.sha1_crypt import sha1_crypt
from model.database_connection import get_database_connection


# /FS010/
def get_current_person(person_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM person WHERE ID = %s", (person_id,))
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
def get_new_person(person_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM person WHERE ID = %s", (person_id,))
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


# /FAN030/
# /FMOF020/
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

    # Mitarbeiter auswählen und geleistete Stunden und Kilometer hinzufügen, falls vorhanden
    cursor.execute("""
        SELECT
            p.ID, 
            p.nachname, 
            p.vorname,
            COALESCE(SUM(TIMESTAMPDIFF(MINUTE , z.start_zeit, z.end_zeit)), 0) AS geleistete_minuten,
            COALESCE(SUM(f.kilometer), 0) AS gefahrene_kilometer,
            p.sperre
        FROM person p
        LEFT JOIN zeiteintrag z ON p.ID = z.mitarbeiter_ID AND EXTRACT(MONTH FROM z.end_zeit) = %s AND EXTRACT(YEAR FROM z.end_zeit) = %s
        LEFT JOIN fahrt f ON z.ID = f.zeiteintrag_ID
        WHERE p.ID = %s
        GROUP BY p.ID
        ORDER BY p.ID ASC
    """, (monat, year, person_id))

    report_table = []
    for row in cursor:
        geleistete_minuten = row[3]
        stunden = geleistete_minuten // 60  # Ganzzahlige Division für Stunden
        minuten = geleistete_minuten % 60  # Rest für Minuten

        report_table.append(
            (
                row[0],  # ID
                row[1],  # Nachname
                row[2],  # Vorname
                f"{stunden}h {minuten}min",  # Geleistete Stunden
                row[4],  # Gefahrene Kilometer
                row[5],
            )
        )

    cursor.close()
    return report_table


# /FAN030/
def account_table(monat, year):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT 
            p.ID, 
            p.nachname, 
            p.vorname,
            COALESCE(TIME_FORMAT(SEC_TO_TIME(SUM(TIMESTAMPDIFF(MINUTE, z.start_zeit, z.end_zeit) * 60)), '%H:%i'), '00:00') AS geleistete_stunden,
            COALESCE(SUM(f.kilometer), 0) AS gefahrene_kilometer,
            p.sperre
        FROM 
            person p
        LEFT JOIN 
            zeiteintrag z ON p.ID = z.mitarbeiter_ID AND EXTRACT(MONTH FROM z.end_zeit) = %s AND EXTRACT(YEAR FROM z.end_zeit) = %s
        LEFT JOIN 
            fahrt f ON z.ID = f.zeiteintrag_id
        WHERE 
            rolle = 'Mitarbeiter'
        GROUP BY 
            p.ID
        ORDER BY 
            p.ID ASC
    """, (monat, year))

    mitarbeiter_table = cursor.fetchall()
    cursor.close()
    return mitarbeiter_table


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


# /FNAN020/
def set_password_required_true(email):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE person SET passwort_erzwingen = 1 WHERE email = %s", (email,))
    connection.commit()
    cursor.close()
    connection.close()


# /FAN060/
def set_password_required_false(email):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE person SET passwort_erzwingen = 0 WHERE email = %s", (email,))
    connection.commit()
    cursor.close()
    connection.close()


# /FV010/
def get_steuerbuero_table():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT ID, nachname, vorname, email, sperre FROM person WHERE rolle = 'Steuerbüro'")
    result = cursor.fetchall()
    return result


# /FV010/
def get_sachbearbeiter_table():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT ID, nachname, vorname, email, sperre FROM person WHERE rolle = 'Sachbearbeiter/Kostenträger'")
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
def edit_account_fct(vorname, nachname, geburtsdatum, qualifikation, adresse, telefonnummer, account_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE person SET vorname = %s, nachname = %s, geburtsdatum = %s, qualifikation = %s, "
                   "adresse = %s, telefonnummer = %s WHERE ID = %s",
                   (vorname, nachname, geburtsdatum, qualifikation, adresse,
                    telefonnummer, account_id))
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


def get_name_by_id(person_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT vorname, nachname FROM person WHERE ID = %s", (person_id,))
    result = cursor.fetchall()
    return result


def sum_hours_mitarbeiter_zeitspanne(start_date, end_date):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT p.ID AS Mitarbeiter_ID, z.klient_ID AS Klient_ID, p.Vorname, p.Nachname, 
        TIME_FORMAT(SEC_TO_TIME(SUM(TIMESTAMPDIFF(MINUTE, z.start_zeit, z.end_zeit) * 60)), '%H:%i') AS anzahl_Stunden 
        FROM person p 
        JOIN zeiteintrag z ON p.ID = z.Mitarbeiter_ID 
        WHERE z.end_zeit BETWEEN %s AND %s 
        GROUP BY p.ID ,z.klient_ID
        ORDER BY p.ID
    """, (start_date, end_date))
    return cursor.fetchall()


def sum_absage_mitarbeiter(start_date, end_date):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT p.ID AS Mitarbeiter_ID, z.klient_ID AS Klient_ID, p.Vorname, p.Nachname, COUNT(z.ID) AS anzahl_Absagen 
        FROM person p 
        JOIN zeiteintrag z ON p.ID = z.Mitarbeiter_ID 
        WHERE z.end_zeit BETWEEN %s AND %s AND z.absage = 1
        GROUP BY p.ID , z.klient_ID
        ORDER BY p.ID
    """, (start_date, end_date))
    return cursor.fetchall()


def sum_km_mitarbeiter(start_date, end_date):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT p.ID AS Mitarbeiter_ID, z.klient_ID AS Klient_ID, p.Vorname, p.Nachname, 
        SUM(f.kilometer) AS gesamt_km, SUM(IF(f.abrechenbar = 1, f.kilometer, 0)) 
        AS abrechenbare_km, SUM(IF(f.abrechenbar = 0, f.kilometer, 0)) AS nichtabrechenbare_km 
        FROM person p 
        JOIN zeiteintrag z ON p.ID = z.Mitarbeiter_ID 
        JOIN fahrt f ON z.ID = f.Zeiteintrag_ID 
        WHERE z.end_zeit BETWEEN %s AND %s
        GROUP BY p.ID , z.klient_ID
        ORDER BY p.ID
    """, (start_date, end_date))
    return cursor.fetchall()


def mitarbeiter_dropdown():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, vorname, nachname FROM person WHERE rolle LIKE '%%Mitarbeiter%%'")
    items = []
    for (ID, vorname, nachname) in cursor.fetchall():
        items.append({'id': ID, 'vorname': vorname, 'nachname': nachname})
    connection.close()
    return items


def kostentraeger_dropdown():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, vorname, nachname FROM person WHERE rolle LIKE '%%Kostenträger%%'")
    items = []
    for (ID, vorname, nachname) in cursor.fetchall():
        items.append({'id': ID, 'vorname': vorname, 'nachname': nachname})
    connection.close()
    return items


def person_dropdown():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, nachname, vorname FROM person WHERE rolle = 'Verwaltung' OR rolle = 'Geschäftsführung'")
    items = []
    for (ID, nachname, vorname) in cursor.fetchall():
        items.append({'id': ID, 'nachname': nachname, 'vorname': vorname})
    connection.close()
    return items


def get_role_by_email(email):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT rolle FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()  # erstes Ergebnis wird aufgerufen
    cursor.close()
    return result[0] if result else None


def get_firstname_by_email(email):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT vorname FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()  # erstes Ergebnis wird aufgerufen
    if result:
        return result[0]
    else:
        return None


def get_lastname_by_email(email):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT nachname FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()  # erstes Ergebnis wird aufgerufen
    if result:
        return result[0]
    else:
        return None


def get_person_id_by_email(email):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()  # erstes Ergebnis wird aufgerufen
    if result:
        return result[0]
    else:
        return None


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
