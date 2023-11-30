from flask import Flask
from einloggen import einloggen_blueprint
from password_reset import password_reset_blueprint

app = Flask(__name__)
app.secret_key = "yor_secret_key"

app.register_blueprint(einloggen_blueprint)
app.register_blueprint(password_reset_blueprint)

if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True)
