import sqlite3
from flask import Flask, redirect, render_template, g, request, session, url_for

from database import connect_db, get_db
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sddadafa'


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite3'):
        g.sqlite_db.close()


def get_current_user():
    user_result = None
    if 'user' in session:
        user = session['user']
        db = connect_db()
        user_query = db.execute(
            'select id, name, password, expert, admin from user where name =?', [user])
        user_result = user_query.fetchone()
    return user_result


@app.route('/')
def home():
    user = get_current_user()
    return render_template('home.html', user=user)


@app.route('/answer')
def answer():
    user = get_current_user()
    db = connect_db()
    cur = db.execute('select id,question_text, asked_id, expert_id from question where expert_id=?', [user['id']])
    questions = cur.fetchall()
    # if request.method == 'POST':
    #     answer = request.form.get('answer')
    #     db.execute('update question set answer_text=?',[answer])
    return render_template('answer.html',questions=questions, user=user)


@app.route('/ask', methods=['POST', 'GET'])
def ask():
    user = get_current_user()
    db = connect_db()
    cur = db.execute('select id, name, expert from user where expert=?', [1])
    experts = cur.fetchall()
    if request.method == 'POST':
        question_text = request.form.get('question_text')
        expert_id = int(request.form.get('expert_id'))
        db.execute('insert into question (question_text,answer_text,asked_id,expert_id) values(?,?,?,?)', [
                   question_text, 'Null', user['id'], expert_id])
        db.commit()
    return render_template('ask.html', experts=experts, user=user)


@app.route('/answer_question/<int:question_id>', methods=['post', 'get'])
def answer_question(question_id):
    db = get_db()
    cursor = db.execute(
        'select id, question_text, answer_text, asked_id, expert_id from question where id=?', [question_id])
    question = cursor.fetchone()
    if request.method=='post':
        answer_text=request.form.get('answer')
        db.execute('update question set answer_text=? where id=?', [answer_text, question_id])  
        db.commit()
    return redirect(url_for('answer'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        request_form = request.form
        name = request_form.get('name')
        password = request_form.get('password')
        db = connect_db()
        get_user = db.execute(
            'select id, name, password from user where name=?', [name])
        user_found = get_user.fetchone()
        if user_found:
            if check_password_hash(user_found['password'], password):
                session['user'] = user_found['name']
                return redirect(url_for('home'))
            else:
                return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/question')
def question():
    return render_template('question.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        request_form = request.form
        name = request_form.get('name')
        password = request_form.get('password')
        hashed_password = generate_password_hash(password, method='sha256')
        db = connect_db()
        db.execute('insert into user (name, password, expert, admin) values (?,?,?,?)', [
                   name, hashed_password, 0, 0])
        db.commit()
    return render_template('register.html')


@app.route('/unanswered')
def unanswered():
    return render_template('unanswered.html')


@app.route('/users')
def users():
    db = get_db()
    cur = db.execute('select id, name, expert from user where admin =?', [0])
    users = cur.fetchall()
    return render_template('users.html', users=users)


@app.route('/change_status/<int:user_id>')
def change_status(user_id):
    db = get_db()
    cursor = db.execute(
        'select id, name, expert from user where id=?', [user_id])
    user = cursor.fetchone()
    if not user['expert']:
        db.execute('update user set expert=? where id=?', [1, user_id])
        db.commit()
    else:
        db.execute('update user set expert=? where id=?', [0, user_id])
        db.commit()
    return redirect(url_for('users'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()
