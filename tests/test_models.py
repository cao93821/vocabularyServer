import unittest
from app import create_app, db
from app.models import User
import time


def user_data_generate():
    user1 = User(user_name='user1', password='123456')
    user2 = User(user_name='user2', password='123456')
    user3 = User(user_name='user3', password='654321')
    db.session.add_all([user1, user2, user3])
    db.session.commit()


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config='test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        user_data_generate()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_unreadable(self):
        user1 = User.query.filter_by(user_name='user1').first()
        with self.assertRaises(AttributeError):
            print(user1.password)

    def test_password_setter(self):
        user1 = User.query.filter_by(user_name='user1').first()
        user2 = User.query.filter_by(user_name='user2').first()
        self.assertTrue(user1.hash_password is not None)
        self.assertTrue(user1.hash_password != user2.hash_password)

    def test_verify_password(self):
        user1 = User.query.filter_by(user_name='user1').first()
        user3 = User.query.filter_by(user_name='user3').first()
        self.assertTrue(user1.verify_password('123456'))
        self.assertFalse(user3.verify_password('123456'))

    def test_token_generate(self):
        user1 = User.query.filter_by(user_name='user1').first()
        self.assertTrue(user1.token_generate() is not None)
        self.assertTrue(user1.token_generate(expiration=1) is not None)

    def test_token_loads(self):
        user1 = User.query.filter_by(user_name='user1').first()
        token1 = user1.token_generate()
        token2 = user1.token_generate(expiration=1)
        token3 = '123456'
        self.assertTrue(User.token_loads(token1) == user1.user_id)
        time.sleep(2)
        self.assertFalse(User.token_loads(token2))
        self.assertFalse(User.token_loads(token3))

