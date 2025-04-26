import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
from werkzeug.utils import secure_filename
from services.data_preparation import prepare_data
from services.eda_analysis import run_eda
from services.statistical_analysis import run_statistical_analysis
from services.ml_modeling import run_ml_modeling
from services.dashboard_generator import generate_hr_dashboard

UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.secret_key = 'supersecretkey'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            output_filename = filename.rsplit('.', 1)[0] + '_dashboard.xlsx'
            output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_filename)
            generate_hr_dashboard(upload_path, output_path)
            return render_template('index.html', download_link=url_for('download_file', filename=output_filename))
        else:
            flash('Invalid file type. Please upload a CSV file.')
            return redirect(request.url)
    return render_template('index.html', download_link=None)

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)