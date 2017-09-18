from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from raven.contrib.flask import Sentry
from config import config


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'web.login'
sentry = Sentry()


def create_app(config_name='develop'):
    """app工厂函数

    :param config_name: 当config='test'的时候启用单元测试的数据库配置
    :return: app
    :rtype: Flask
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    login_manager.init_app(app)
    Bootstrap(app)
    if config_name != 'test':
        sentry.init_app(app, app.config['SENTRY_DSN'])
    from app.views.api_version130 import main
    from app.views.api_version140 import api_version140
    from app.views.web import web
    app.register_blueprint(web)
    app.register_blueprint(main)
    app.register_blueprint(api_version140, url_prefix='/api_version140')

    return app

