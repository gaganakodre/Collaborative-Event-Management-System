from flask import Flask
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from controllers.login_controller import auth
from controllers.events_controller import events  # Uncomment when you create event controller

app = Flask(__name__)

# Configurations
app.config["JWT_SECRET_KEY"] = "your-secret-key"
app.config['SWAGGER'] = {
    'title': 'My API',
    'uiversion': 3
}

# Initialize Swagger and JWT
swagger = Swagger(app)
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(events)  # Register event routes when ready

@app.route("/")
def home():
    return {"message": "Hello from API"}

if __name__ == "__main__":
    app.run(debug=True)
