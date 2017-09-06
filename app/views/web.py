import logging

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user

from app import db, login_manager
from app.models import Vocabulary, User
from app.forms import LoginForm, SignupForm


web = Blueprint('web', __name__)


# 初始化一个logger
logger = logging.Logger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter('name: %(name)s\nlevel: %(levelname)s\n%(message)s\n'))
logger.addHandler(handler)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter_by(user_id=user_id).first()


@web.route('/')
@web.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('.vocabulary', user_id=current_user.user_id))
    else:
        return redirect(url_for('.login'))


@web.route('/vocabulary/<user_id>')
@login_required
def vocabulary(user_id):
    page = request.args.get('page', default=1, type=int)
    pagination = db.session.query(Vocabulary).\
        filter_by(user_id=user_id, is_remember=False).\
        paginate(page, per_page=20, error_out=False)
    words = [(index_number, word) for index_number, word in enumerate(pagination.items)]
    return render_template('index.html', words=words, pagination=pagination, current_page='vocabulary')


@web.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_name=form.user_name.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.is_remember.data)
            logger.debug('login succeed')
            return redirect(url_for('.vocabulary', user_id=user.user_id))
    return render_template('login.html', current_page='login', form=form)


@web.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('.index'))


@web.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if User.query.filter_by(user_name=form.user_name.data).first():
            return redirect(url_for('.signup'))
        user = User(user_name=form.user_name.data, password=form.password.data)
        db.session.add(user)
        login_user(user)
        return redirect(url_for('.vocabulary', user_id=user.user_id))
    return render_template('signup.html', current_page='signup', form=form)


@web.route('/remember/<word_id>')
def remember():
    pass
