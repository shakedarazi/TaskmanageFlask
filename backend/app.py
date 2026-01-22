import os
from flask import Flask
from flask_cors import CORS
from db import init_db
from auth_routes import auth_bp
from task_routes import task_bp
from ai_routes import ai_bp
from datetime import timedelta
from limiter_config import limiter
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("voltify.log"),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
CORS(app, origins=["http://localhost:8000"], supports_credentials=True) #TODO: Remember to add origins - the domain of the deployed frontend
init_db(app)
limiter.init_app(app)


app.secret_key = os.getenv('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
if os.environ.get("FLASK_ENV") == "production":
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = "None"
else:
    app.config['SESSION_COOKIE_SECURE'] = False #TODO: Check about changing it to True when deploying.
    app.config['SESSION_COOKIE_SAMESITE'] = "Lax"

app.config['SESSION_COOKIE_DOMAIN'] = 'localhost'
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_HTTPONLY'] = False


app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(task_bp, url_prefix="/api/tasks")
app.register_blueprint(ai_bp, url_prefix="/api/ai")

@app.route("/")
def index():
    return {"message": "Voltify Task Manager API"}, 200

@app.after_request
def log_cors_headers(response):
    print("➡️ Access-Control-Allow-Credentials:", response.headers.get("Access-Control-Allow-Credentials"))
    print("➡️ Access-Control-Allow-Origin:", response.headers.get("Access-Control-Allow-Origin"))
    print("➡️ Response status code:", response.status_code)
    return response

if __name__ == "__main__":
    app.run(debug=True)