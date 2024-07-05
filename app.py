from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vocab.db'
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(80), nullable=False)
    meaning = db.Column(db.String(120), nullable=False)
    pronunciation = db.Column(db.String(120), nullable=True)  # 発音記号を追加
    example_sentence = db.Column(db.String(255), nullable=True)  # 例文を追加
    difficulty = db.Column(db.Float, default=0.5)
    correct_count = db.Column(db.Integer, default=0)
    total_count = db.Column(db.Integer, default=0)

@app.route('/')
def index():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        username = user.username
    else:
        username = None
    return render_template('index.html', username=username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/add_word', methods=['GET', 'POST'])
def add_word():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        word_text = request.form['word']
        meaning = request.form['meaning']
        pronunciation = request.form.get('pronunciation', '')
        example_sentence = request.form.get('example_sentence', '')
        new_word = Word(word=word_text, meaning=meaning, pronunciation=pronunciation, example_sentence=example_sentence)
        db.session.add(new_word)
        db.session.commit()
        return redirect(url_for('index'))
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        username = user.username
    else:
        username = None
    return render_template('add_word.html', username=username)

@app.route('/quiz', methods=['POST'])
def quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_answer = request.json['answer']
    correct_answer = request.json['correct_answer']
    word_id = request.json['word_id']
    word = Word.query.get(word_id)
    word.total_count += 1
    if user_answer == correct_answer:
        word.correct_count += 1
        word.difficulty = max(0.1, word.difficulty - 0.1)
    else:
        word.difficulty = min(1.0, word.difficulty + 0.1)
    db.session.commit()
    return jsonify(success=True)

@app.route('/api/words', methods=['GET'])
def api_words():
    words = Word.query.all()
    words_list = [{'id': word.id, 'word': word.word, 'meaning': word.meaning, 'difficulty': word.difficulty} for word in words]
    return jsonify(words_list)

@app.route('/api/word/<int:word_id>', methods=['GET'])
def api_word_detail(word_id):
    word = Word.query.get(word_id)
    if word:
        word_detail = {
            'word': word.word,
            'meaning': word.meaning,
            'pronunciation': word.pronunciation,
            'example_sentence': word.example_sentence
        }
        return jsonify(word_detail)
    return jsonify({'error': 'Word not found'}), 404

@app.route('/word_list')
def word_list():
    words = Word.query.all()
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        username = user.username
    else:
        username = None
    return render_template('word_list.html', words=words, username=username)

if __name__ == '__main__':
    app.run(debug=True)
