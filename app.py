from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_FILE_SIZE
from pdf_processor import generate_pdf, extract_data, process_uploaded_file

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['GET', 'POST'])
def convert():
    if request.method == 'POST':
        content_type = request.form.get('content_type')
        
        if content_type == 'text':
            text_content = request.form.get('content')
            if not text_content:
                flash('Please enter some text', 'error')
                return redirect(request.url)
            
            filename = f"text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = generate_pdf(text_content, filename)
            flash('PDF generated successfully!', 'success')
            return redirect(url_for('dashboard'))

        elif content_type == 'url':
            url = request.form.get('content')
            if not url:
                flash('Please enter a URL', 'error')
                return redirect(request.url)
            
            filename = f"url_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = generate_pdf(url, filename, 'url')
            flash('PDF generated from URL successfully!', 'success')
            return redirect(url_for('dashboard'))

        elif content_type == 'file':
            if 'file' not in request.files:
                flash('No file selected', 'error')
                return redirect(request.url)
            
            file = request.files['file']
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                if file.content_length > MAX_FILE_SIZE:
                    flash('File is too large (max 10MB)', 'error')
                    return redirect(request.url)
                
                try:
                    pdf_path, file_info = process_uploaded_file(file)
                    flash('File processed successfully!', 'success')
                    return redirect(url_for('dashboard'))
                except Exception as e:
                    flash(f'Error processing file: {str(e)}', 'error')
                    return redirect(request.url)
            else:
                flash('Invalid file type', 'error')
                return redirect(request.url)

    return render_template('convert.html')

@app.route('/dashboard')
def dashboard():
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.lower().endswith('.pdf'):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file_info = {
                'name': filename,
                'size': f"{os.path.getsize(filepath) / 1024:.1f} KB",
                'date': datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M'),
                'download_url': url_for('download_file', filename=filename)
            }
            files.append(file_info)
    
    return render_template('dashboard.html', files=files)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error='404 - Page Not Found'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error='500 - Internal Server Error'), 500

if __name__ == '__main__':
    app.run(debug=True)