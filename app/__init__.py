import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from config import Config


# find best language by comparing client provided weights svs. languages application supports
def get_locale():
    return request.accept_languages.best_match(current_app.config["LANGUAGES"])


# initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.login"
login.login_message = _l("Please log in to access this page")
mail = Mail()
moment = Moment()
babel = Babel()


def create_app(config_class=Config):
    """Application factory."""

    app = Flask(__name__) # initialize Flask app
    app.config.from_object(config_class)

    # bind extensions to Flask app
    db.init_app(app)
    migrate.init_app(app)
    login.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    # register blueprints to Flask app
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.health import bp as health_bp
    app.register_blueprint(health_bp)

    from app.meals import bp as meals_bp
    app.register_blueprint(meals_bp)

    from app.profile import bp as profile_bp
    app.register_blueprint(profile_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    # when in production, log errors by email
    if not app.debug and not app.testing:
        if app.config["MAIL_SERVER"]:
            
            auth = None
            if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
                auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            
            secure = None
            if app.config["MAIL_USE_TLS"]:
                secure = ()
            
            # add email handler instance to Flask logger object (app.logger)
            mail_handler = SMTPHandler(
                mailhost = (app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr = "no-reply@" + app.config["MAIL_SERVER"],
                toaddrs = app.config["ADMINS"],
                subject = "Steady Failure",
                credentials = auth,
                secure = secure
            )
            mail_handler.setLevel(logging.ERROR) # set mail handler instance to only report errors
            app.logger.addHandler(mail_handler) # attach mail handler to Flask logger object 
        
        # file logging for failure conditions that do not end in a Python exception 
        if not os.path.exists("logs"):
            os.mkdir("logs")
            file_handler = RotatingFileHandler("logs/steady.log", maxBytes=10240, backupCount=10)
            # from LogRecord attributes ; timestamp, logging level, logged message, source file, and line number
            file_handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info("Steady startup")

    return app

from app import models




