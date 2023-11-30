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


