from flask import Flask, request, redirect, url_for, render_template, send_from_directory, session
import os
from werkzeug.utils import secure_filename

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
    return render_template('admin.html', files=files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run()