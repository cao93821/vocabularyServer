from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

db = SQLAlchemy()
app = Flask(__name__)
db.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:yiwen517112@139.196.77.131/vocabulary_test'
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

from . import views, models
