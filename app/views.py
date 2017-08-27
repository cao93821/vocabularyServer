from app import db
from flask import request, abort, Blueprint
from .models import Vocabulary, User
import json
import logging
from functools import wraps

main = Blueprint('main', __name__)

# 初始化一个logger
logger = logging.Logger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter('%(name)20s: %(levelname)5s\n%(message)s'))
logger.addHandler(handler)


def request_log(func):
    """装饰器函数，用于生成请求信息的log"""
    @wraps(func)
    def decorator(*args, **kwargs):
        logger.debug('request header: \n{} request content: {}'.format(request.headers, request.data))
        return func(*args, **kwargs)
    return decorator


@main.route('/word', methods=['POST'])
@request_log
def word_add():
    """向自己的单词本当中添加单词"""
    request_content = request.json
    new_word = Vocabulary(
        user_id=request_content['user_id'],
        word=request_content['word'],
        word_explain=request_content['explain']
    )
    db.session.add(new_word)
    db.session.commit()
    return 'success'


@main.route('/words', methods=['GET'])
@request_log
def words_get():
    """获取自己单词本当中的所有单词"""
    token = json.loads(request.json)['token']
    user_id = User.token_loads(token)
    if not user_id:
        abort(404)
    words = db.session.query(Vocabulary).filter_by(user_id=user_id, is_remember=False).all()
    words_dict = dict(((word.id, dict(word=word.word,
                                      word_explain=word.word_explain,
                                      is_remember=word.is_remember
                                      )) for word in words))
    return json.dumps(words_dict)


@main.route('/word/<word_id>', methods=['PUT'])
@request_log
def word_remember(word_id):
    """将一个单词标记为is_remember = True"""
    word = db.session.query(Vocabulary).filter_by(id=word_id).first()
    word.is_remember = True
    db.session.commit()
    return 'success'


@main.route('/register', methods=['POST'])
@request_log
def register():
    """注册账号"""
    request_content = json.loads(request.json)
    if request_content['username'] and request_content['password']:
        if db.session.query(User).filter_by(user_name=request_content['username']).first():
            abort(403)
        else:
            new_user = User(user_name=request_content['username'], password=request_content['password'])
            db.session.add(new_user)
            db.session.commit()
            token = db.session.query(User).filter_by(user_name=request_content['username']).first().token_generate()
            return json.dumps({'token': token.decode('utf-8')})


@main.route('/login', methods=['POST'])
@request_log
def login():
    """登录"""
    request_content = json.loads(request.json)
    user = db.session.query(User).filter_by(user_name=request_content['username']).first()
    if user:
        if not user.verify_password(request_content['password']):
            abort(403)
        return json.dumps({'token': user.token_generate().decode('utf-8')})




