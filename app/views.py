from app import app, db
from flask import request, abort
from .models import Vocabulary, User
import json


@app.route('/word', methods=['POST'])
def word_add():
    request_content = request.json
    new_word = Vocabulary(user_id=request_content['user_id'],
                          word=request_content['word'],
                          word_explain=request_content['explain'])
    db.session.add(new_word)
    db.session.commit()
    return 'success'


@app.route('/words', methods=['GET'])
def words_get():
    words = db.session.query(Vocabulary).filter_by(user_id=1, is_remember=False).all()
    words_dict = dict(((word.id, dict(word=word.word,
                                      word_explain=word.word_explain,
                                      is_remember=word.is_remember)) for word in words))
    return json.dumps(words_dict)


@app.route('/word/<word_id>', methods=['PUT'])
def word_remember(word_id):
    word = db.session.query(Vocabulary).filter_by(id=word_id).first()
    word.is_remember = True
    db.session.commit()
    return 'success'


@app.route('/register', methods=['POST'])
def register():
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


@app.route('/login', methods=['POST'])
def login():
    request_content = json.loads(request.json)
    user = db.session.query(User).filter_by(user_name=request_content['username']).first()
    if not user.verify_password(request_content['password']):
        abort(403)
    else:
        return json.dumps({'token': user.token_generate().decode('utf-8')})




