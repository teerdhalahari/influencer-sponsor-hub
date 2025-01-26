from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sponsors.sqlite3'
app.config['SECRET_KEY'] = '75689bfgu45th'
csrf = CSRFProtect(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "login" 


from application import routes, model

@login_manager.user_loader
def load_user(user_id):
    return model.User.query.get(int(user_id))

# Ensure application context is pushed
with app.app_context():
    if not path.exists("C:/Users/M TEERDHA/OneDrive/Desktop/mad1/instance/sponsors.sqlite3"):
        db.create_all()
        a = model.User(username="admin1", email="abc@gmail.com", password=generate_password_hash("123"), role="admin")
        db.session.add(a)
        db.session.commit()
        print("database created")
