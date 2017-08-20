from fabric.api import *

# 使用远程命令的用户名
env.user = 'phamnuwen'
# 执行命令的服务器
env.hosts = ['139.196.77.131']


def pack():
    local('python setup.py sdist --formats=gztar', capture=False)


def deploy():
    dist = local('python setup.py --fullname', capture=True).strip()
    put('dist/{}.tar.gz'.format(dist), '/tmp/vocabulary.tar.gz')
    run('mkdir /tmp/vocabulary')
    with cd('/tmp/vocabulary'):
        run('tar xzf /tmp/vocabulary.tar.gz')
        with cd('/tmp/vocabulary/{}/'.format(dist)):
            run('/home/phamnuwen/myproject/vocabularyServer/venv/bin/python setup.py install')
    run('rm -rf /tmp/vocabulary /tmp/vocabulary.tar.gz')
    with cd('/home/phamnuwen/myproject/vocabularyServer'):
        # run('venv/bin/python run.py db init')
        # run('venv/bin/python run.py db migrate')
        # run('venv/bin/python run.py db upgrade')
        run('venv/bin/python run.py runserver -h "0.0.0.0" &')