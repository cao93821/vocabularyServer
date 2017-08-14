from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)
db.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:yiwen517112@139.196.77.131/vocabulary_test'


from . import views, models
