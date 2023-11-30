from flask import Flask
from einloggen import einloggen_blueprint
from password_reset import password_reset_blueprint
from logout import logout_blueprint

app = Flask(__name__)
app.secret_key = "your_secret_key"

app.register_blueprint(einloggen_blueprint)
app.register_blueprint(password_reset_blueprint)
app.register_blueprint(logout_blueprint)


if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True)
