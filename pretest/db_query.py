import mysql.connector

def fetch_data():
    cnx = mysql.connector.connect(
        host="localhost",
        user="username",
        password="password",
        database="dbname"
    )
    cursor = cnx.cursor()

    query = """
    SELECT
        clients.client_id, clients.last_name,
        employees.employee_id, employees.last_name
    FROM
        clients
    INNER JOIN
        employees ON clients.client_id = employees.employee_id
    """
    cursor.execute(query)

    for (client_id, client_last_name, employee_id, employee_last_name) in cursor:
        print("Client ID: {}, Client Last Name: {}, Employee ID: {}, Employee Last Name: {}".format(client_id, client_last_name, employee_id, employee_last_name))

    cursor.close()
    cnx.close()

if __name__ == "__main__":
    fetch_data()