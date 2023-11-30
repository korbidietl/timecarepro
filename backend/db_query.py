import mysql.connector
from databaseConnection import get_database_connection
from passlib.hash import sha1_crypt
from passlib.utils import generate_password


# Ludwig: @Korbi was das? xD
# kann ersetzt werden, wenn wir get password / role / name  etc. by email haben
def get_user_by_email(email):
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)  # Aktiviere dictionary-based Cursor
    cursor.execute("SELECT * FROM person WHERE email = %s", (email,))
    user = cursor.fetchone()  # erstes Ergebnis wird aufgerufen
    cursor.close()
    connection.close()
    return user

# Bitte anlegen: def get_password_for_user(email): -> rename: validate_login
# Methode validate_login mit der E-Mail-Adresse und dem Passwort des Benutzers aufrufen.
# Diese Methode gibt True zurück,
# wenn die E-Mail-Adresse und das Passwort in der Datenbank vorhanden sind und korrekt sind.
# Andernfalls gibt sie False zurück.
def validate_login(self, email, password):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT passwort FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()  # erstes Ergebnis wird aufgerufen
    if result:
        hashed_password = result[0]
        if sha1_crypt.verify(password, hashed_password):
            return True
    return False

# Bitte anlegen: def get_role_for_user(email):
# Methode, die die Rolle basierend auf der E-Mail aus der Datenbank abruft.
# Wenn ein Ergebnis gefunden wird, wird es als Rolle (str) zurückgegeben. Andernfalls wird None zurückgegeben.
def get_role_by_email(self, email):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT rolle FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()  # erstes Ergebnis wird aufgerufen
    cursor.close()
    return result[0] if result else None

# Bitte anlegen: def get_surnmae_for_user(email):
# Methode gibt Vornamen zurück, wenn er in der Datenbank gefunden wird. Andernfalls gibt sie None zurück.
def get_firstname_by_email(self, email):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT vorname FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()  # erstes Ergebnis wird aufgerufen
    if result:
        return result[0]
    else:
        return None


# Aktualisiert das Passwort eines Nutzers in der Datenbank.
# hasht es mit SHA1 und speichert das gehashte Passwort in der Datenbank.
# Anschließend wird das neue Passwort zurückgegeben.
def reset_password(self, email):
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
def validate_email(self, email):
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
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT sperre FROM person WHERE email = %s", (email,))
    result = cursor.fetchone()
    if result:
        if result[0] == 1:
            return True
    return False


# @korbi bitte anpassen/löschen/ hab ich glaub ich oben schon
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
