from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/create_account', methods=['POST'])
def register_account():
    # Hier kannst du die Daten aus dem Formular verwenden
    lastname = request.form.get('lastname')
    firstname = request.form.get('firstname')
    role = request.form.get('role')
    email = request.form.get('email')

    # Hier füge die Logik zum Verarbeiten der Formulardaten hinzu

    return render_template('success.html')  # Hier kannst du eine Erfolgsseite anzeigen lassen
