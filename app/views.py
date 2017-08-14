from app import app, db
from flask import request
from .models import Vocabulary, User


@app.route('/word', methods=['POST'])
def word_add():
    request_content = request.json
    new_word = Vocabulary(user_id=request_content['user_id'], word=request_content['word'])
    db.session.add(new_word)
    db.session.commit()
    return 'ok'
