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

    def reset_password(self, email):
        connection = self.get_connection()
        cursor = connection.cursor()
        new_password = generate_password(10)
        hashed_password = sha1_crypt.encrypt(new_password)
        cursor.execute("UPDATE person SET passwort = %s, passwort_erzwingen = 1 WHERE email = %s", (hashed_password, email,))
        connection.commit()
        return new_password
