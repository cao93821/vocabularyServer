import unittest
import os

from flask_migrate import MigrateCommand, Migrate
from flask_script import Manager

# 不得不放在这个位置以使COV先于blueprint等的初始化启动
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from app import db, create_app


app = create_app()
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def test(cover=False):
    if cover and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        # os.execvp用来开启一个新程序代替现在的程序，sys.executable是指运行程序
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        # 下面都是为了print出coverage报告的绝对路径
        print('Coverage Summary:')
        # 这个语句在任何情况下获取绝对路径
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://{}/index.html'.format(covdir))
        COV.erase()


if __name__ == '__main__':
    manager.run()



