import mysql.connector

servername = 'localhost'
username = 'grup3sql'
password = 'skill59UP86VM'
dbname = 'timecarepro'


def get_database_connection():
    try:
        conn = mysql.connector.connect(host=servername, user=username, password=password, database=dbname)

        if conn.is_connected():
            print('Erfolgreich mit der Datenbank verbunden')

    except mysql.connector.Error as e:
        print(f"Fehler bei der Verbindung zur Datenbank: {e}")

    return conn


def close_database_connection(conn):
    if conn and conn.is_connected():
        conn.close()
        print('Verbindung zur Datenbank geschlossen.')


