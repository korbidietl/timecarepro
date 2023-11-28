import mysql.connector

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
        print("Client ID: {}, Client Last Name: {}, Employee ID: {}, Employee Last Name: {}".format(client_id, client_last_name, employee_id, employee_last_name))

    cursor.close()
    cnx.close()

if __name__ == "__main__":
    fetch_data()