from flask import Flask
from config import Config
from .models import db, User
from flask_migrate import Migrate
from flask_login import LoginManager
from .auth.routes import auth
from .api import api
from .ig import ig
from flask_moment import Moment
from flask_cors import CORS


migrate = Migrate()
login_manager = LoginManager()
moment = Moment()
# cors = CORS(origins=['http://shoha.com', ''])
cors = CORS()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

login_manager.login_view = 'auth.loginPage'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app,db)
    login_manager.init_app(app)
    moment.init_app(app)
    cors.init_app(app)

    app.register_blueprint(auth)
    app.register_blueprint(api)
    app.register_blueprint(ig)

    return app
