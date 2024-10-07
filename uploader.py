import os
import time
from uuid import uuid4
from functools import wraps
from flask import Flask, render_template, session, request, redirect, url_for
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or "pepegaman123pepegaman123"

UPLOADS_FOLDER = Path('uploads/')

@app.template_filter('hsize')
def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

@app.template_filter('ctime')
def timectime(s):
    return time.ctime(s)

@app.template_filter('path_normalize')
def path_normalize(s):
    while '//' in s:
        s = s.replace('//', '/')
    return s

def session_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'id' not in session:
            session['id'] = str(uuid4())

        session.permanent = True

        # create user folder if it doesn't exist
        p = UPLOADS_FOLDER / session['id']
        if not p.exists():
            p.mkdir(parents=True)

        return f(*args, **kwargs)
    return decorated

@app.route("/", methods=['GET', 'POST'])
@session_required
def main():
    path = request.args.get('path')
    if path is None:
        return redirect(url_for('main', path="/"))

    path += '/'

    # filter out LFI stuff
    orig_path = path
    path = path.replace('../', '')
    prev = str(Path(path).parent)
    
    full_path_str = str(UPLOADS_FOLDER / session['id']) + path
    full_path = Path(full_path_str)

    # redirect back to root if this file/folder doesn't exist
    if not full_path.exists():
        return redirect(url_for('main', path="/"))

    # if this is a file, print it out
    if full_path.is_file():
        return render_template("file.html", name=full_path.name, contents=full_path.read_text())

    if request.method == 'POST':
        if 'dirname' in request.form:
            dirname = secure_filename(request.form['dirname'])
            new_dir = full_path / dirname
            if not new_dir.exists():
                new_dir.mkdir()

        if 'file' in request.files:
            file = request.files['file']
            
            # no empty filename
            if file.filename == '':
                abort(400)

            filename = secure_filename(file.filename)
            file.save(str(UPLOADS_FOLDER / session['id'] / filename))

    # we want file name, size, date modified, and if it's a directory
    files = [p for p in full_path.iterdir()]
    names = [f.name for f in files]
    stats = [f.stat() for f in files]
    is_dir = [f.is_dir() for f in files]
    combined = [(f, s, d) for f, s, d in zip(names, stats, is_dir)]
    combined.sort(key=lambda x: x[0])

    return render_template("index.html", files=combined, prev=prev, path=orig_path)

if __name__ == '__main__':
    import logging
    from waitress import serve
    logging.getLogger('waitress').setLevel(logging.DEBUG)
    serve(app, host="0.0.0.0", port=8000)
