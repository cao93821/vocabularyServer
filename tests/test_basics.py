import unittest
from app import create_app, db
from flask import current_app


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name='test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.create_all()
        self.app_context.pop()

    def test_test_is_working(self):
        self.assertTrue(True)

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['SQLALCHEMY_DATABASE_URI'] ==
                        'mysql://root:yiwen517112@139.196.77.131/vocabulary_unittest')
