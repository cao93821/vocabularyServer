from functools import wraps
import logging
import json

from app import db
from flask import request, abort, Blueprint
from .models import Vocabulary, User
from sqlalchemy.exc import DBAPIError

main = Blueprint('main', __name__)

# 初始化一个logger
logger = logging.Logger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter('name: %(name)s\nlevel: %(levelname)s\n%(message)s\n'))
logger.addHandler(handler)


# def request_log(func):
#     """装饰器函数，用于生成请求信息的log"""
#     @wraps(func)
#     def decorator(*args, **kwargs):
#         logger.debug('request header: \n{} request content: {}'.format(request.headers, request.data))
#         return func(*args, **kwargs)
#     return decorator


@main.before_request
def request_inspection():
    """对于非json请求统一返回417错误码"""
    request_content = request.json
    if not request_content:
        logger.error('request mimetype is {}'.format(request.headers))
        # http-code 417表示请求标头不支持，有可能是是使用mimetype不正确，或者请求体为空
        abort(417)


@main.before_request
def request_debug_log():
    """对于所有的request记录日志以方便debug"""
    request_data = request.data
    logger.info('request data is {}'.format(request_data))


@main.after_request
def response_debug_log(response):
    """对于所有的response记录日志以方便debug"""
    response_data = response.data
    logger.info('response data is {}'.format(response_data))
    return response


@main.errorhandler(DBAPIError)
def database_error(error):
    request_content = request.json
    logger.error('DBAPIError: request json = {}'.format(request_content))
    return 'database error', 400


@main.route('/word', methods=['POST'])
def word_add():
    """向自己的单词本当中添加单词"""
    request_content = request.json
    try:
        new_word = Vocabulary(
            user_id=request_content['user_id'],
            word=request_content['word'],
            word_explain=request_content['explain']
        )
    except (KeyError, TypeError) as e:
        logger.error('{}: request json = {}'.format(type(e), request_content))
        # http-code 400表示请求的内容有误
        return 'failed', 400
    else:
        db.session.add(new_word)
        db.session.commit()
        return 'success', 200


@main.route('/words', methods=['GET'])
def words_get():
    """获取自己单词本当中的所有单词"""
    token = json.loads(request.json)['token']
    user_id = User.token_loads(token)
    if not user_id:
        return 'wrong token', 404
    user = db.session.query(User).filter_by(user_id=user_id).first()
    if not user:
        logger.error('user_id = {}'.format(user_id))
        return 'user is not exist', 404
    words = user.vocabulary.filter_by(is_remember=False).all()
    words_dict = dict(((word.id, dict(word=word.word,
                                      word_explain=word.word_explain,
                                      is_remember=word.is_remember
                                      )) for word in words))
    return json.dumps(words_dict)


@main.route('/word/<word_id>', methods=['PUT'])
def word_remember(word_id):
    """将一个单词标记为is_remember = True"""
    word = db.session.query(Vocabulary).filter_by(id=word_id).first()
    if not word:
        logger.error('word_id = {}'.format(word_id))
        return 'word is not exist', 400
    word.is_remember = True
    db.session.commit()
    return 'success', 200


@main.route('/register', methods=['POST'])
def register():
    """注册账号"""
    request_content = json.loads(request.json)
    if request_content['username'] and request_content['password']:
        if db.session.query(User).filter_by(user_name=request_content['username']).first():
            return 'user name is already exist', 400
        else:
            new_user = User(user_name=request_content['username'], password=request_content['password'])
            db.session.add(new_user)
            db.session.commit()
            token = db.session.query(User).filter_by(user_name=request_content['username']).first().token_generate()
            return json.dumps({'token': token.decode('utf-8')})


@main.route('/login', methods=['POST'])
def login():
    """登录"""
    request_content = json.loads(request.json)
    user = db.session.query(User).filter_by(user_name=request_content['username']).first()
    if not user:
        return 'user name is wrong', 444
    if not user.verify_password(request_content['password']):
        return 'password is wrong', 445
    # 由于token_generate()返回的是binary，因此需要做decode
    return json.dumps({'token': user.token_generate().decode('utf-8')})




