from flask import Flask, request, redirect, url_for, render_template, send_from_directory, send_file, session
import os
import zipfile
from datetime import datetime
from werkzeug.utils import secure_filename
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'hwp', 'hwpx', 'xlsx', 'xls', 'xlsm', 'doc', 'docx', 'pdf', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        uploader = request.form.get('uploader', '').strip()
        files = request.files.getlist('file')

        if not uploader:
            return redirect(url_for('upload', success=0))

        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
        folder_name = f"{timestamp}_{uploader}"
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
        os.makedirs(folder_path, exist_ok=True)

        for f in files:
            if f and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                f.save(os.path.join(folder_path, filename))

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

    folders = sorted(os.listdir(app.config['UPLOAD_FOLDER']), reverse=True)
    grouped_folders = {}
    for folder in folders:
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
        if os.path.isdir(folder_path):
            grouped_folders[folder] = os.listdir(folder_path)

    return render_template('admin.html', grouped_folders=grouped_folders)

@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/download_zip/<folder_name>')
def download_zip(folder_name):
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{folder_name}.zip")

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

    return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
