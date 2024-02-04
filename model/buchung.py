from model.database_connection import get_database_connection


# /FGF030/
# /FV120/
def get_last_buchung(client_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT DATE_FORMAT(monat, '%Y-%m') as Monat, id FROM buchung 
        WHERE klient_id = %s 
        ORDER BY monat DESC 
        LIMIT 1
    """, (client_id,))
    return cursor.fetchone()


# /FGF030/
def delete_buchung(buchung_id):
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM buchung WHERE id = %s", (buchung_id,))
    connection.commit()


# /FAN040/
# /FMOF030/
# /FMOF050/
def check_month_booked(datum, client_id):
    date_month = datum.strftime('%m')
    date_year = datum.strftime('%Y')
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM buchung WHERE EXTRACT(MONTH FROM monat) = %s AND EXTRACT(YEAR FROM monat) = %s "
                   "AND klient_ID = %s",
                   (date_month, date_year, client_id,))
    result = cursor.fetchone()
    if result:
        return True
    return False
