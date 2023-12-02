from flask import Flask, render_template, request
from db_query import sachbearbeiter_dropdown

app = Flask(__name__)


@app.route('/create_client', methods=['POST'])
def register_client():
    lastname = request.form.get('lastname')
    firstname = request.form.get('firstname')
    birthday = request.form.get('birthday')
    number = request.form.get('number')
    request.form.get('sbDropdown')

    sachbearbeiter_dropdown()

    return render_template('create_client.html', item=sachbearbeiter_dropdown())


if __name__ == '__main__':
    app.run(debug=True)
