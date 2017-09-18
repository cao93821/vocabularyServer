import logging

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user, login_user, logout_user

from app import db, login_manager
from app.models import Vocabulary, User
from app.forms import LoginForm, SignupForm


web = Blueprint('web', __name__)


# 初始化一个logger
logger = logging.Logger(__name__)
logger.setLevel(logging.ERROR)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter('name: %(name)s\nlevel: %(levelname)s\n%(message)s\n'))
logger.addHandler(handler)


@login_manager.user_loader
def load_user(user_id):
    """flask-login使用的加载用户的回调函数"""
    return db.session.query(User).filter_by(user_id=user_id).first()


@web.before_request
def request_debug_log():
    """记录所有进来的请求"""
    logger.debug('request header: {}'.format(request.headers))


@web.after_request
def response_debug_log(response):
    """记录所有出去的响应"""
    logger.debug('response header: {}'.format(response.headers))
    return response


@web.route('/')
@web.route('/index')
def index():
    """主页"""
    if current_user.is_authenticated:
        return redirect(url_for('.vocabulary', user_id=current_user.user_id))
    else:
        return redirect(url_for('.login'))


@web.route('/vocabulary/<user_id>')
@login_required
def vocabulary(user_id):
    """单词列表"""
    page = request.args.get('page', default=1, type=int)
    # 合理的代码分行格式
    pagination = db.session.query(
        Vocabulary
    ).filter_by(
        user_id=user_id,
        is_remember=False
    ).paginate(
        page,
        per_page=20,
        error_out=False
    )
    words = [(20 * (page - 1) + index_number + 1, word) for index_number, word in enumerate(pagination.items)]
    return render_template('index.html', words=words, pagination=pagination, current_page='vocabulary')


@web.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_name=form.user_name.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.is_remember.data)
            logger.debug('login succeed')
            flash('登录成功')
            return redirect(url_for('.vocabulary', user_id=user.user_id))
        else:
            flash('用户名或密码错误')
            return redirect(url_for('.login'))

    return render_template('login.html', current_page='login', form=form)


@web.route('/logout')
@login_required
def logout():
    """登出功能"""
    logout_user()
    return redirect(url_for('.index'))


@web.route('/signup', methods=['GET', 'POST'])
def signup():
    """注册页面"""
    form = SignupForm()
    if form.validate_on_submit():
        if User.query.filter_by(user_name=form.user_name.data).first():
            flash('该用户名已被使用')
            return redirect(url_for('.signup'))
        user = User(user_name=form.user_name.data, password=form.password.data)
        db.session.add(user)
        user = User.query.filter_by(user_name=user.user_name).first()
        login_user(user)
        flash('注册成功')
        return redirect(url_for('.vocabulary', user_id=user.user_id))
    return render_template('signup.html', current_page='signup', form=form)


@web.route('/<page>/remember/<word_id>')
@login_required
def remember(word_id, page):
    """记住单词的功能"""
    word = Vocabulary.query.filter_by(id=word_id).first()
    if current_user != word.owner:
        abort(403)
    word.is_remember = True
    db.session.commit()
    logger.debug('word {} remember success, current status {}'.format(word.word, word.is_remember))
    return redirect(url_for('.vocabulary', user_id=current_user.user_id, page=page))
