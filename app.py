from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import subprocess

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vulnweb.db"
app.config['SECRET_KEY'] = 'your_secret_key' 
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Users.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if Users.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
        else:
            new_user = Users(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first.', 'danger')
        return redirect(url_for('login'))
    user = Users.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/notes', methods=['GET', 'POST'])
def notes():
    output = ''
    if request.method == 'POST':
        title = request.form.get('title', '')
        message = request.form.get('message', '')
        try:
            if message:
                result = subprocess.run(message, shell=True, capture_output=True, text=True)
                output = result.stdout + result.stderr
                print(output)
                if "not found" in output:
                    output = ""
            flash('Success Send Note To Admin!', 'success')
        except Exception as e:
            flash('Failed to execute command.', 'danger')
            output = str(e)
    return render_template('notes.html', output=output)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=8000)