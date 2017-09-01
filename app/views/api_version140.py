from functools import wraps
import logging
import json

from app import db
from flask import request, abort, Blueprint, url_for
from ..models import Vocabulary, User
from sqlalchemy.exc import DBAPIError

api_version140 = Blueprint('api_version140', __name__)

# 初始化一个logger
logger = logging.Logger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter('name: %(name)s\nlevel: %(levelname)s\n%(message)s\n'))
logger.addHandler(handler)


def token_verify(func):
    """装饰器函数，用于对有token验证要求的路由验证token是否可用

    version 1.4.0新增
    """
    # 下面的表达式decorator = wraps(func)(decorator)
    # wraps(func)返回的是一个update_wraps函数，其wrapped值为func，其作用是将穿进去的函数的函数名改为func
    # 因此调用decorator之后就可以将decorator的__name__等值修改为func的
    # 这样flask在内省路由函数的时候生成的endpoint就不会是'decorator'
    @wraps(func)
    def decorator(*args, **kwargs):
        request_content = request.json
        try:
            token = request_content['token']
        except KeyError:
            logger.error("can't find token error! json is {}".format(str(request_content)))
            # 403 forbidden
            return 'can not find token', 403
        user_id, is_token_new = User.token_loads(token)
        user = db.session.query(User).filter_by(user_id=user_id).first()
        if not user:
            return 'token is wrong', 403
        # 如果token需要更新，则在视图函数返回的HTTP content当中插入新的token
        elif not is_token_new:
            new_token = user.token_generate()
            view_return = func(*args, **kwargs)
            return_json = json.loads(view_return[0])
            # 警告！！！不要使用str()对bytes进行转换，因为str只是显示bytes的字面量，要使用decode才行
            return_json['new_token'] = new_token.decode('utf-8')
            return json.dumps(return_json), view_return[1], view_return[2]
        # 必须要return，否则调用者无法收到路由函数的响应
        return func(*args, **kwargs)
    return decorator


@api_version140.before_request
def request_inspection():
    """对于非json请求统一返回417错误码"""
    request_content = request.json
    if not request_content:
        logger.error('request mimetype is {}'.format(request.headers))
        # http-code 417表示请求标头不支持，有可能是是使用mimetype不正确，或者请求体为空
        abort(417)


@api_version140.before_request
def request_debug_log():
    """对于所有的request记录日志以方便debug"""
    request_data = request.data
    logger.info('request data is {}'.format(request_data))


@api_version140.after_request
def response_debug_log(response):
    """对于所有的response记录日志以方便debug"""
    response_data = response.data
    logger.info('response data is {}'.format(response_data))
    return response


@api_version140.errorhandler(DBAPIError)
def database_error(error):
    request_content = request.json
    logger.error('DBAPIError: request json = {}'.format(request_content))
    return 'database error', 400


@api_version140.route('/words', methods=['POST'])
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


@api_version140.route('/words', methods=['GET'])
@token_verify
def words_get():
    """获取自己单词本当中的所有单词"""
    token = request.json['token']
    user_id = User.token_loads(token)[0]
    user = db.session.query(User).filter_by(user_id=user_id).first()
    if not user:
        logger.error('user_id = {}'.format(user_id))
        return 'user is not exist', 404
    # .args是werkzeug下定义的一个MultiDict，其get方法支持定义类型
    page = request.args.get('page', 1, type=int)
    paginate = user.vocabulary\
        .filter_by(is_remember=False)\
        .order_by(Vocabulary.id)\
        .paginate(page, per_page=20, error_out=False)
    # 由于是在非浏览器环境下，必须使用完整的url才能进行跳转，所以要将_external设置为True
    words_list = [dict(
        url=url_for('.word_remember', word_id=word.id, _external=True),
        word=word.word,
        word_explain=word.word_explain,
        is_remember=word.is_remember
    ) for word in paginate.items]
    page_number = list(paginate.iter_pages())
    # 为了使用装饰器增加token，无法使用jsonify
    return json.dumps({'words': words_list, 'page_number': page_number}), 200, {'mimetype': 'application/json'}


@api_version140.route('/words/<word_id>', methods=['PUT'])
@token_verify
def word_remember(word_id):
    """将一个单词标记为is_remember = True"""
    word = db.session.query(Vocabulary).filter_by(id=word_id).first()
    if not word:
        logger.error('word_id = {}'.format(word_id))
        return 'word is not exist', 400
    word.is_remember = True
    db.session.commit()
    return json.dumps({'description': 'success'}), 200, {'mimetype': 'application/json'}


@api_version140.route('/register', methods=['POST'])
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


@api_version140.route('/login', methods=['POST'])
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




