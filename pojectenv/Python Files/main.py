from flask import Flask, request, session, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db' # nur zu Testzwecken
app.secret_key = 'your secret key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

class TimeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
    user = db.relationship('User', backref=db.backref('time_entries', lazy=True))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'),
        nullable=False)
    project = db.relationship('Project', backref=db.backref('time_entries', lazy=True))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/start', methods=['POST'])
def start():
    project_id = request.form.get('project_id')
    entry = TimeEntry(user_id=session['user_id'], project_id=project_id)
    db.session.add(entry)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop():
    entry_id = request.form.get('entry_id')
    entry = TimeEntry.query.get(entry_id)
    entry.end_time = datetime.utcnow()
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/')
def index():
    entries = TimeEntry.query.filter_by(user_id=session.get('user_id')).all()
    return render_template('index.html', entries=entries)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

