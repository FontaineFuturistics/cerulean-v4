from flask import Flask, render_template, request, redirect, url_for, session
from cerulean_v4.db import get_db, create_user, validate_user, get_mappings, add_mapping, remove_mapping
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change_this_secret') # TODO make this a real key later

def levenshtein(a, b):
    if a == b:
        return 0
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)
    v0 = [i for i in range(len(b) + 1)]
    v1 = [0] * (len(b) + 1)
    for i in range(len(a)):
        v1[0] = i + 1
        for j in range(len(b)):
            cost = 0 if a[i] == b[j] else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        v0, v1 = v1, v0
    return v0[len(b)]

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'signup' in request.form: # TODO: for some reason you need to provide a username to even be redirected to signup, fix that
            return redirect(url_for('signup'))
        username = request.form['username']
        password = request.form['password']
        user = validate_user(username, password)
        if user:
            session['username'] = username
            return redirect(url_for('mappings'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username.isalnum():
            return render_template('signup.html', error='Usernames may not contains special characters')
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

@app.route('/mappings', methods=['GET', 'POST'])
def mappings():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    if request.method == 'POST':
        action = request.form.get('action')
        urn = request.form.get('urn')
        url_val = request.form.get('url')
        if action == 'add' and urn and url_val:
            add_mapping(username, urn, url_val)
        elif action == 'remove' and urn:
            remove_mapping(username, urn)
    mappings = get_mappings(username)
    return render_template('mappings.html', username=session['username'], mappings=mappings)

# Syntax: /search?u=<username>&q=<query>
@app.route('/search')
def search():
    username = request.args.get('u')
    query = request.args.get('q')
    if not username or not query:
        return "Missing username or query", 400
    mappings = get_mappings(username)
    if not mappings:
        return "No mappings found for user", 404
    closest_urn = min(mappings.keys(), key=lambda urn: levenshtein(urn, query))
    return redirect(mappings[closest_urn])

def main():
    app.run(host='0.0.0.0', port=8080) # Change to 443 for HTTPS when I implement that

if __name__ == '__main__':
    main()
