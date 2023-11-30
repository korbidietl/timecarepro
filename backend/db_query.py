import mysql.connector
from databaseConnection import get_database_connection
from passlib.hash import sha1_crypt
from passlib.utils import generate_password


# Ludwig: @Korbi was das? xD
def get_user_by_email(email):
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)  # Aktiviere dictionary-based Cursor
    query = "SELECT * FROM person WHERE email = %s"
    cursor.execute(query, (email,))
    user = cursor.fetchone()  # Hole nur den ersten Treffer
    cursor.close()
    connection.close()
    return user


# Bitte anlegen: def get_password_for_user(email): -> rename: validate_login
# Methode validate_login mit der E-Mail-Adresse und dem Passwort des Benutzers aufrufen.
# Diese Methode gibt True zurück,
# wenn die E-Mail-Adresse und das Passwort in der Datenbank vorhanden sind und korrekt sind.
# Andernfalls gibt sie False zurück.
def validate_login(email, password):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT passwort FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()
    if result:
        hashed_password = result[0]
        if sha1_crypt.verify(password, hashed_password):
            return True
    return False


# Bitte anlegen: def get_role_for_user(email):

# Bitte anlegen: def get_surnmae_for_user(email):

# Bitte anlegen: def set_password_for_user(password, email)
# Passwort zurückzusetzen Methode reset_password mit der E-Mail-Adresse des Benutzers aufrufen.
# Diese Methode generiert ein neues Passwort
# hasht es mit SHA1 und speichert das gehashte Passwort in der Datenbank.
# Anschließend wird das neue Passwort zurückgegeben.
def reset_password(email):
    connection = get_database_connection()
    cursor = connection.cursor()
    new_password = generate_password(10)
    hashed_password = sha1_crypt.encrypt(new_password)
    cursor.execute("UPDATE person SET passwort = %s, passwort_erzwingen = 1 WHERE email = %s",
                   (hashed_password, email,))
    connection.commit()
    return new_password


# Überprüfung, ob eine Benutzer-ID für die gegebene E-Mail-Adresse existiert.
# Wenn dies der Fall ist, gibt die Methode True zurück, sonst False.
def validate_email(email):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()
    if result:
        return True
    return False

# Bitte anlegen: def get_locked_status(email):
# Überprüfung, ob der Benutzer, der die gegebene E-Mail-Adresse hat, gesperrt ist.
# Wenn der Wert des Feldes "sperre" 1 ist, gibt die Methode True zurück, was bedeutet,
# dass das Benutzerkonto gesperrt ist. Andernfalls gibt die Methode False zurück.
def check_account_locked(self, email):
    connection = self.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT sperre FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()
    if result:
        if result[0] == 1:
            return True
    return False





def fetch_data():
    cnx = mysql.connector.connect(
        host="localhost",
        user="grup3sql",
        password="skill59UP86VM",
        database="timecarepro"
    )
    cursor = cnx.cursor()

    query = """
    SELECT
        klient.ID, klient.nachname,
        person.ID, person.nachname
    FROM
        klient
    INNER JOIN
        person ON klient.ID = person.ID
    """
    cursor.execute(query)

    for (client_id, client_last_name, employee_id, employee_last_name) in cursor:
        print("Client ID: {}, Client Last Name: {}, Employee ID: {}, Employee Last Name: {}".format(client_id,
                                                                                                    client_last_name,
                                                                                                    employee_id,
                                                                                                    employee_last_name))

    cursor.close()
    cnx.close()


if __name__ == "__main__":
    fetch_data()


def update_password_for_user(email, new_password_hash):
    cnx = get_database_connection()
    cursor = cnx.cursor()
    query = "UPDATE person SET password = %s WHERE email = %s"
    cursor.execute(query, (new_password_hash, email))
    cnx.commit()
    cursor.close()
    cnx.close()


def get_password_hash_for_user(email):
    cnx = get_database_connection()
    cursor = cnx.cursor()
    query = "SELECT password FROM person WHERE email = %s"
    cursor.execute(query, (email,))
    password_hash = cursor.fetchone()
    cursor.close()
    cnx.close()
    return password_hash[0] if password_hash else None
