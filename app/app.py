from flask import Flask, request, redirect, render_template_string, send_file
import os, sqlite3, re, string, random, tempfile, subprocess

app = Flask(__name__)
DB_PATH = '/data/bookmarks.db'

def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS mappings (
            user_id TEXT,
            keyword TEXT,
            url TEXT,
            PRIMARY KEY (user_id, keyword),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

def get_user_id():
    dn = request.environ.get('SSL_CLIENT_S_DN', '')
    match = re.search(r'CN=([A-Za-z0-9]{4})', dn)
    return match.group(1) if match else None

@app.route('/', methods=['GET', 'POST'])
def manage():
    init_db()
    user_id = get_user_id()
    if not user_id:
        return '''
        <h2>Create Your Identity Certificate</h2>
        <form method="post" action="/keygen">
            <button type="submit">Download Certificate</button>
        </form>
        '''
    with sqlite3.connect(DB_PATH) as db:
        db.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
        if request.method == 'POST':
            db.execute("INSERT OR REPLACE INTO mappings (user_id, keyword, url) VALUES (?, ?, ?)",
                       (user_id, request.form['keyword'], request.form['url']))
        mappings = db.execute("SELECT keyword, url FROM mappings WHERE user_id=? ORDER BY rowid DESC",
                              (user_id,)).fetchall()
    html = f"<h2>Welcome, User {user_id}</h2><form method='post'>"
    html += "Keyword: <input name='keyword'> URL: <input name='url'> <button>Add</button></form><ul>"
    for kw, url in mappings:
        html += f"<li>{kw} → <a href='{url}' target='_blank'>{url}</a> "
        html += f"<a href='/delete?kw={kw}'><img src='/trash.png' width='16'></a></li>"
    html += "</ul>"
    return html

@app.route('/delete')
def delete():
    user_id = get_user_id()
    kw = request.args.get('kw')
    if user_id and kw:
        with sqlite3.connect(DB_PATH) as db:
            db.execute("DELETE FROM mappings WHERE user_id=? AND keyword=?", (user_id, kw))
    return redirect('/')

@app.route('/keygen', methods=['POST'])
def keygen():
    id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    tmp = tempfile.mkdtemp()
    key = os.path.join(tmp, f'{id}.key.pem')
    csr = os.path.join(tmp, f'{id}.csr.pem')
    crt = os.path.join(tmp, f'{id}.crt.pem')
    p12 = os.path.join(tmp, f'{id}.p12')
    ca_key = '/etc/ssl/ca/ca.key.pem'
    ca_crt = '/etc/ssl/ca/ca.crt.pem'
    subprocess.run(['openssl', 'genrsa', '-out', key, '2048'])
    subprocess.run(['openssl', 'req', '-new', '-key', key, '-subj', f'/CN={id}', '-out', csr])
    subprocess.run(['openssl', 'x509', '-req', '-in', csr, '-CA', ca_crt, '-CAkey', ca_key,
                    '-CAcreateserial', '-days', '365', '-out', crt])
    subprocess.run(['openssl', 'pkcs12', '-export', '-out', p12, '-inkey', key, '-in', crt,
                    '-certfile', ca_crt, '-passout', 'pass:'])
    return send_file(p12, as_attachment=True, download_name=f'{id}.p12')

@app.route('/search')
def search():
    usr = request.args.get('usr')
    q = request.args.get('q')
    with sqlite3.connect(DB_PATH) as db:
        rows = db.execute("SELECT keyword, url FROM mappings WHERE user_id=?", (usr,)).fetchall()
    mapping = dict(rows)
    if q in mapping:
        return f"<meta http-equiv='refresh' content='0;url={mapping[q]}'>"
    # Fuzzy match
    margin = int(len(q) * 0.3)
    distances = {kw: levenshtein(q, kw) for kw in mapping}
    closest = [kw for kw, d in distances.items() if d <= margin]
    if len(closest) == 1:
        return f"<meta http-equiv='refresh' content='0;url={mapping[closest[0]]}'>"
    html = f"<h3>No exact match for “{q}”. Closest:</h3><ul>"
    for kw in closest[:10]:
        html += f"<li><a href='/search?usr={usr}&q={kw}'>{kw} → {mapping[kw]}</a></li>"
    html += "</ul>"
    return html

def levenshtein(a, b):
    if len(a) < len(b): return levenshtein(b, a)
    if len(b) == 0: return len(a)
    prev = list(range(len(b)+1))
    for i, ca in enumerate(a):
        curr = [i+1]
        for j, cb in enumerate(b):
            cost = 0 if ca == cb else 1
            curr.append(min(curr[-1]+1, prev[j+1]+1, prev[j]+cost))
        prev = curr
    return prev[-1]
