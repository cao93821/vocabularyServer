from app import db, app


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20))
    vocabulary = db.relationship('Vocabulary', backref='owner')


class Vocabulary(db.Model):
    __tablename__ = 'vocabulary'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    word = db.Column(db.String(20))

# app.app_context().push()
# db.create_all()
