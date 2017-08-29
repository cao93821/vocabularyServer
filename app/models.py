from app import db
from itsdangerous import TimedJSONWebSignatureSerializer, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20))
    hash_password = db.Column(db.String(100))
    vocabulary = db.relationship('Vocabulary', backref='owner', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('Password not readable')

    @password.setter
    def password(self, password):
        self.hash_password = generate_password_hash(password)

    def verify_password(self, password):
        """验证密码是否正确

        :param password: 用于检验的密码
        :type password: str
        :return: True or False
        """
        return check_password_hash(self.hash_password, password)

    def token_generate(self, expiration=3600):
        """将秘钥和用户user_id进行序列化，生成一个有超时时间的token

        :param expiration: 超时时间，单位为秒
        :return: token
        :rtype: bytes
        """
        signature = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expiration)
        return signature.dumps({'user_id': self.user_id})

    @staticmethod
    def token_loads(token):
        """将用户传递过来的token进行反序列化

        :param token: 用于反序列化的token™
        :return: user_id(int) or False
        """
        signature = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = signature.loads(token)['user_id']
        except BadSignature or SignatureExpired:
            return False
        return user_id


class Vocabulary(db.Model):
    __tablename__ = 'vocabulary'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    word = db.Column(db.String(20))
    word_explain = db.Column(db.Text)
    is_remember = db.Column(db.Boolean, default=False)
