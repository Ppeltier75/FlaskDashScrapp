from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
import os

# Configuration de l'application Flask
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, '..', 'instance', 'Dashboard.db')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SECRET_KEY'] = 'Rayzodu75017.'
IMG_FOLDER = os.path.join("static", "IMG")
app.config["UPLOAD_FOLDER"] = IMG_FOLDER

# Initialisation des extensions Flask
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

# Importation des modèles et des routes après la création de 'app' et 'db'
from Dashboard import models
from Dashboard import routes

# Création des tables de base de données si elles n'existent pas
with app.app_context():
    db.create_all()

# Lancement de l'application Dash 
from Dashboard.dashboardapp import create_dash_application
dash_app = create_dash_application(app)

