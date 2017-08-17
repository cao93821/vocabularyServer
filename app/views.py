from app import app, db
from flask import request
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
