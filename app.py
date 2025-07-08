from flask import Flask, request, redirect, url_for, render_template, send_from_directory, session
import os
from werkzeug.utils import secure_filename
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secretkey'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'hwp', 'hwpx', 'xlsx', 'xls', 'xlsm', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return redirect(url_for('upload'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        files = request.files.getlist('file')
        for f in files:
            if f and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('upload', success=1))
    return render_template('upload.html', success=request.args.get('success'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '4113':
            session['authenticated'] = True
        else:
            return render_template('admin_login.html', error=True)

    if not session.get('authenticated'):
        return render_template('admin_login.html')

    files = os.listdir(app.config['UPLOAD_FOLDER'])
    files.sort(key=lambda f: os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], f)), reverse=True)

    grouped_files = defaultdict(list)
    for f in files:
        timestamp = os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], f))
        dt = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:00')
        grouped_files[dt].append(f)

    return render_template('admin.html', grouped_files=grouped_files)


if __name__ == '__main__':
    app.run()
