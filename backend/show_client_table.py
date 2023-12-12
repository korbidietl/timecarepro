from flask import Flask, render_template, request, session
from db_query import client_dashboard
# ... (weitere erforderliche Importe)

app = Flask(__name__)

@app.route('/klienten', methods=['GET', 'POST'])
def show_clients():
    # Wenn der Request eine POST-Anfrage ist, holen wir den gewählten Monat
    if request.method == 'POST':
        monat = request.form.get('zeitraum')
    else:
        # Standardmäßig wird der aktuelle Monat ausgewählt, falls keine Auswahl getroffen wurde
        monat = None  # oder setze einen Standardmonat, z.B. datetime.now().month

    clients = client_dashboard(monat)

    if not clients:
        return render_template('klienten.html', no_clients_message=True)

    # Rendern der HTML-Seite mit den Klientendaten
    user_role = session.get('user_role')  # Hole die Benutzerrolle aus der Session
    return render_template('klienten.html', clients=clients, user_role=user_role)

if __name__ == '__main__':
    app.run(debug=True)
