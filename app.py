from flask import Flask, render_template, request, redirect, url_for
import os
import fitz  # PyMuPDF
import google.generativeai as genai
from io import BytesIO

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file):
    text = ''
    doc = fitz.open(None, file)
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    job_description = request.form.get('job_description')  # Retrieve job description from form
    if file.filename == '' or job_description == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        file.seek(0)  # Move the file cursor to the beginning
        if file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(BytesIO(file.read()))
            genai.configure(api_key='GOOGLE API HERE')  
            model = genai.GenerativeModel('gemini-pro')
            
            # Generate summary from resume
            response_resume = model.generate_content([
                text,
                "Summary of the document.\n"
                "Skills: What skills this person has.\n"
                "Total years of experience: Number of years of experience.\n"
                "Number of companies worked for: Number of companies.\n"
                "Names of the companies: List of company names.\n"
                "Designations in those companies: List of designations.\n"
                "Projects worked on: List of projects.\n"
                "Programming languages known: List of programming languages.\n"
                "Extras: Any additional information."
            ])
            summary_resume = response_resume.candidates[0].content.parts[0].text
            
            # Analyze the similarity between job description and summary using the generative model
            response_similarity = model.generate_content([
                job_description,
                summary_resume,
                "Should we hire this person for the role and what is the percentage of similarity his resume have with the job description and if we should hire him then why and if we should not then why?, provide the text in plain normal format"
            ])
            fit_percentage = response_similarity.candidates[0].content.parts[0].text
            print(fit_percentage)
            
            return render_template('response.html', fit_percentage=fit_percentage)
        else:
            return 'File uploaded successfully (not a PDF)'
    else:
        return 'Invalid file format'

if __name__ == '__main__':
    app.run()
