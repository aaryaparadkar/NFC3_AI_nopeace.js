import base64
import io
from nltk.corpus import stopwords
from PyPDF2 import PdfReader
import google.generativeai as genai
from flask import Flask, request, jsonify
import nltk
from difflib import SequenceMatcher
import requests
from bs4 import BeautifulSoup as bs
import warnings

app = Flask(__name__)

warnings.filterwarnings("ignore", module='bs4')



nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

stop_words = set(stopwords.words('english'))

# Configure Gemini API
genai.configure(api_key='AIzaSyAIwKBkgpCokD1KwwpyW7jH1U2910XQZkU')

# def decode_pdf(base64_pdf: str) -> str:
#     try:
#         pdf_content = base64.b64decode(base64_pdf)
#         pdf_reader = PdfReader(io.BytesIO(pdf_content))
#         text = ""
#         for page in pdf_reader.pages:
#             text += page.extract_text()
#         return text
#     except Exception as e:
#         return f"Error decoding PDF: {str(e)}"

def summarize_pdf_with_gemini(base64_pdf: str) -> str:
    pdf_text = decode_pdf_content(base64_pdf)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Please provide a concise summary of the following text, highlighting the main points and key ideas:\n\n{pdf_text}"
    response = model.generate_content(prompt)
    return response.text

def purifyText(string):
    words = nltk.word_tokenize(string)
    return (" ".join([word for word in words if word.lower() not in stop_words]))

def searchBing(query, num):
    url = 'https://www.bing.com/search?q=' + query
    urls = []
    page = requests.get(url, headers={'User-agent': 'John Doe'})
    soup = bs(page.text, 'html.parser')
    for link in soup.find_all('a'):
        url = str(link.get('href'))
        if url.startswith('http') and not url.startswith(('http://go.m', 'https://go.m')):
            urls.append(url)
    return urls[:num]

def extractText(url):
    page = requests.get(url)
    soup = bs(page.text, 'html.parser')
    return soup.get_text()

def webVerify(string, results_per_sentence):
    sentences = nltk.sent_tokenize(string)
    matching_sites = []
    for url in searchBing(query=string, num=results_per_sentence):
        matching_sites.append(url)
    for sentence in sentences:
        for url in searchBing(query=sentence, num=results_per_sentence):
            matching_sites.append(url)
    return list(set(matching_sites))

def similarity(str1, str2):
    return (SequenceMatcher(None, str1, str2).ratio()) * 100

def report(text):
    matching_sites = webVerify(purifyText(text), 2)
    matches = {}
    for i in range(len(matching_sites)):
        matches[matching_sites[i]] = similarity(text, extractText(matching_sites[i]))
    return dict(sorted(matches.items(), key=lambda item: item[1], reverse=True))

@app.route('/api/plagiarism', methods=['POST'])
def check_plagiarism():
    data = request.json
    if not data or 'pdf' not in data:
        return jsonify({'error': 'No PDF data provided'}), 400
    
    base64_pdf = data['pdf']
    text = decode_pdf_content(base64_pdf)
    if text.startswith("Error decoding PDF"):
        return jsonify({'error': text}), 400
    
    result = report(text)
    return jsonify(result)

@app.route('/api/similarity', methods=['POST'])
def check_similarity():
    data = request.json
    if not data or 'pdf1' not in data or 'pdf2' not in data:
        return jsonify({'error': 'Both pdf1 and pdf2 are required'}), 400
    j1 = data['pdf1']
    #print(j1)
    j2 = data['pdf2']
    #print(j2)  
    text1 = decode_pdf_content(j1)
    print(text1,"JAMAL MUSIALA")
    text2 = decode_pdf_content(j2)
    print(text2,"SIDDHU MUSIALA")
    if text1.startswith("Error decoding PDF") or text2.startswith("Error decoding PDF"):
        return jsonify({'error': 'Error decoding one or both PDFs'}), 400
    
    similarity_score = similarity(text1, text2)
    return jsonify({'similarity': similarity_score})

@app.route('/api/summarize', methods=['POST'])
def summarize_pdf():
    data = request.json
    if not data or 'pdf' not in data:
        return jsonify({'error': 'No PDF data provided'}), 400
    
    base64_pdf = data['pdf']
    summary = summarize_pdf_with_gemini(base64_pdf)
    return jsonify({'summary': summary})

def decode_pdf_content(base64_pdf: str) -> str:
    """Decode the base64 PDF and extract its text content."""
    try:
        pdf_content = base64.b64decode(base64_pdf)
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error decoding PDF: {str(e)}"

@app.route('/api/decode', methods=['POST'])
def decode_pdf_route():
    data = request.json
    if not data or 'pdf' not in data:
        return jsonify({'error': 'No PDF data provided'}), 400
    
    base64_pdf = data['pdf']
    decoded_text = decode_pdf_content(base64_pdf)
    return jsonify({'decoded_text': decoded_text})

if __name__ == '__main__':
    app.run(debug=True)