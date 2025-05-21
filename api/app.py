from flask import Flask
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from controllers.login_controller import auth

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "your-secret-key"
swagger = Swagger(app)
jwt = JWTManager(app)

app.register_blueprint(auth)

@app.route("/")
def home():
    return {"message": "Hello from API"}

if __name__ == "__main__":
    app.run(debug=True)
