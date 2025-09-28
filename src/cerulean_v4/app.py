from flask import Flask, render_template, request, redirect, url_for, session
from cerulean_v4.db import get_db, create_user, validate_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change_this_secret') # TODO make this a real key later

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'signup' in request.form:
            return redirect(url_for('signup'))
        username = request.form['username']
        password = request.form['password']
        user = validate_user(username, password)
        if user:
            session['username'] = username
            return redirect(url_for('welcome'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if create_user(username, password):
            return redirect(url_for('login'))
        else:
            return render_template('signup.html', error='Username already exists')
    return render_template('signup.html')

@app.route('/welcome')
def welcome():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('welcome.html', username=session['username'])

def main():
    app.run(host='0.0.0.0', port=8080) # Change to 443 for HTTPS when I implement that

if __name__ == '__main__':
    main()
