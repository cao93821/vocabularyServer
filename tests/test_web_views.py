import unittest

from flask import url_for

from app import create_app, db
from app.models import User, Vocabulary


def user_data_generate():
    user1 = User(user_name='user1', password='123456')
    user2 = User(user_name='user2', password='123456')
    word1 = Vocabulary(owner=user1, word='hello')
    word2 = Vocabulary(owner=user1, word='hi')
    db.session.add_all([user1, word1, word2, user2])
    db.session.commit()


class ViewsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name='test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        user_data_generate()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, user_name, password):
        self.client.post('/login', data=dict(
            user_name=user_name,
            password=password
        ), follow_redirects=True)

    def logout(self):
        self.client.get('/logout', follow_redirects=True)

    def test_index(self):
        response = self.client.get(url_for('web.index'))
        self.assertTrue(response.status_code == 302)
        self.assertTrue('login' in response.headers.get('Location'))
        self.login('user1', '123456')
        response = self.client.get(url_for('web.index'))
        self.assertFalse('login' in response.headers.get('Location'))
        self.assertTrue('vocabulary' in response.headers.get('Location'))

    def test_vocabulary(self):
        self.login('user1', '123456')
        user = db.session.query(User).filter_by(user_name='user1').first()
        response = self.client.get(url_for('web.vocabulary', user_id=user.user_id))
        self.assertTrue('欢迎来到猪猪单词本' in response.get_data(as_text=True))

    def test_login(self):
        response = self.client.post(url_for('web.login'), data=dict(
            user_name='user1',
            password='123456'
        ))
        self.assertTrue('vocabulary' in response.headers.get('Location'))
        self.logout()

        response = self.client.post(url_for('web.login'), data=dict(
            user_name='user3',
            password='123456'
        ))
        self.assertTrue('login' in response.headers.get('Location'))

        response = self.client.post(url_for('web.login'), data=dict(
            user_name='user1',
            password='654321'
        ))
        self.assertTrue('login' in response.headers.get('Location'))

    def test_logout(self):
        self.login('user1', '123456')
        response = self.client.get(url_for('web.logout'))
        self.assertTrue(response.status_code == 302)
        self.assertTrue('index' in response.headers.get('Location'))

    def test_signup(self):
        response = self.client.get(url_for('web.signup'))
        self.assertTrue('注册' in response.get_data(as_text=True))

        response = self.client.post(url_for('web.signup'), data=dict(
            user_name='user3',
            password='123456'
        ))
        self.assertTrue(response.status_code == 302)
        self.assertTrue('vocabulary' in response.headers.get('Location'))
        self.assertTrue(User.query.filter_by(user_name='user3').first())
        self.logout()

        response = self.client.post(url_for('web.signup'), data=dict(
            user_name='user1',
            password='123456'
        ))
        self.assertTrue(response.status_code == 302)
        self.assertTrue('signup' in response.headers.get('Location'))

    def test_remember(self):
        self.login('user1', '123456')
        user = User.query.filter_by(user_name='user1').first()
        word = Vocabulary.query.filter_by(user_id=user.user_id, is_remember=False).first()
        response = self.client.get(url_for('web.remember', page=1, word_id=word.id))
        self.assertTrue(response.status_code == 302)
        self.assertTrue('vocabulary' in response.headers.get('Location'))
        word_after = Vocabulary.query.filter_by(id=word.id).first()
        self.assertTrue(word_after.is_remember)
        self.logout()

        self.login('user2', '123456')
        user = User.query.filter_by(user_name='user1').first()
        word = Vocabulary.query.filter_by(user_id=user.user_id, is_remember=False).first()
        response = self.client.get(url_for('web.remember', page=1, word_id=word.id))
        self.assertTrue(response.status_code == 403)
