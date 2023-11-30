import mysql.connector
from passlib.hash import sha1_crypt
from passlib.utils import generate_password


class MySQLOperations:

    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def get_connection(self):
        connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        return connection

    # Methode validate_login mit der E-Mail-Adresse und dem Passwort des Benutzers aufrufen.
    # Diese Methode gibt True zurück,
    # wenn die E-Mail-Adresse und das Passwort in der Datenbank vorhanden sind und korrekt sind.
    # Andernfalls gibt sie False zurück.
    def validate_login(self, email, password):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT passwort FROM person WHERE email = %s", (email,))
        result = cursor.fetchone()
        if result:
            hashed_password = result[0]
            if sha1_crypt.verify(password, hashed_password):
                return True
        return False

    # Passwort zurückzusetzen Methode reset_password mit der E-Mail-Adresse des Benutzers aufrufen.
    # Diese Methode generiert ein neues Passwort
    # hasht es mit SHA1 und speichert das gehashte Passwort in der Datenbank.
    # Anschließend wird das neue Passwort zurückgegeben.
    def reset_password(self, email):
        connection = self.get_connection()
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
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM person WHERE email = %s", (email,))
        result = cursor.fetchone()
        if result:
            return True
        return False

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
