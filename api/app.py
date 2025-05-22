from flask import Flask
from flask_jwt_extended import JWTManager
from flasgger import Swagger

from controllers.login_controller import auth
from controllers.events_controller import events
from controllers.collaborative_controller import collaboration
from controllers.versionhistory_controller import version_history

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "your-secret-key"
app.config['SWAGGER'] = {
    'title': 'My API',
    'uiversion': 3
}

swagger = Swagger(app)
jwt = JWTManager(app)

app.register_blueprint(auth)
app.register_blueprint(events)
app.register_blueprint(collaboration)
app.register_blueprint(version_history)

@app.route("/")
def home():
    return {"message": "Hello from Collaborative-Event-Management-System API Documentation with Swagger! Kindly please append '/apidocs' under the base URL above to access the documentation."}


