class Config:
    SECRET_KEY = 'yiwen517112'
    SENTRY_DSN = 'http://ee86ced8316543eea5ceee794ba4908a:26c443db80364a1584cfd3fed7120332@139.196.77.131:9000/11'


class DevelopConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:yiwen517112@139.196.77.131/vocabulary_test'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:yiwen517112@139.196.77.131/vocabulary_test'


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:yiwen517112@139.196.77.131/vocabulary_unittest'
    WTF_CSRF_ENABLED = False


config = {
    'develop': DevelopConfig,
    'production': ProductionConfig,
    'test': TestConfig,
    'default': DevelopConfig
}
