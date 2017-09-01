from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config='develop'):
    """app工厂函数

    :param config: 当config='test'的时候启用单元测试的数据库配置
    :return: app
    :rtype: Flask
    """
    app = Flask(__name__)
    db.init_app(app)
    if config == 'test':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:yiwen517112@139.196.77.131/vocabulary_unittest'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:yiwen517112@139.196.77.131/vocabulary_test'
    app.config['SECRET_KEY'] = 'yiwen517112'
    from app.views.api_version130 import main
    from app.views.api_version140 import api_version140
    app.register_blueprint(main)
    app.register_blueprint(api_version140, url_prefix='/api_version140')

    return app

