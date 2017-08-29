import unittest
import sys

from app import db, create_app
from flask_migrate import MigrateCommand, Migrate
from flask_script import Manager


app = create_app()
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


def test():
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        test()
    else:
        manager.run()