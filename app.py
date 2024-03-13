from flask import Flask, render_template, request, redirect, url_for
import os
import fitz  # PyMuPDF
import google.generativeai as genai

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    text = ''
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        if file_path.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
            genai.configure(api_key='AIzaSyArLPSqQsvFK3_sXbLHMxx6U3hfomsZ8J4')  # Replace 'YOUR_API_KEY' with your actual API key
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content([text, "Summary of this document, please"])
            summary_text = response.candidates[0].content.parts[0].text
            print("---------- Summary ----------")
            print(summary_text)  # Print generated summary text
            with open('summary.txt', 'w') as f:
                f.write(summary_text)
            return 'Summary written to summary.txt'  # Optional success message
        else:
            return 'File uploaded successfully (not a PDF)'
    else:
        return 'Invalid file format'

if __name__ == '__main__':
    app.run()
