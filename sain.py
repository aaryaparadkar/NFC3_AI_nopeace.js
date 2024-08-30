import base64
import io
from PyPDF2 import PdfReader
import google.generativeai as genai
import requests
from copyleaks.copyleaks import Copyleaks
from copyleaks.models.submit.document import FileDocument
#from copyleaks.models import SubmissionProperties

# Assuming 'YOUR_GEMINI_API_KEY' is the actual key
genai.configure(api_key='AIzaSyAIwKBkgpCokD1KwwpyW7jH1U2910XQZkU')

COPYLEAKS_EMAIL = 'manasmishra101010@gmail.com'
COPYLEAKS_API_KEY = '58a8344f-6d73-4af5-973e-c575e9c0f045'

def encode_pdf(path: str) -> str:
    """Encode a PDF file to base64."""
    with open(path, "rb") as pdf:
        pdf_bytes = pdf.read()
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    return base64_pdf

def decode_pdf(base64_pdf: str) -> str:
    """Decode the base64 PDF and extract its text content."""
    try:
        # Decode the base64-encoded PDF
        pdf_content = base64.b64decode(base64_pdf)
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        text = ""  #base64 pdf content
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error decoding PDF: {str(e)}"
    

def summarize_pdf_with_gemini(base64_pdf: str) -> str:
    """Summarize the PDF content using Gemini API."""
    pdf_text = decode_pdf(base64_pdf)
    
    # Initialize Gemini model
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Generate summary
    prompt = f"Please provide a concise summary of the following text, highlighting the main points and key ideas:\n\n{pdf_text}"
    response = model.generate_content(prompt)
    
    return response.text

# Example usage
pdf_path = 'manas.pdf'

# Encode the PDF
encoded_pdf = encode_pdf(pdf_path)
print(encoded_pdf)

summary = summarize_pdf_with_gemini(encoded_pdf)
'''

#Checking plagiriasm
def check_plagiarism_with_copyleaks(base64_pdf: str) -> str:
    """Check plagiarism using Copyleaks API."""
    try:
        # Initialize Copyleaks
        auth = Copyleaks.login(COPYLEAKS_EMAIL, COPYLEAKS_API_KEY)
        if auth:
            print('messi')
        else:
            print('that bitch')
        
        # Decode PDF content
        pdf_content = base64.b64decode(base64_pdf)
        
        # Create a temporary file
        with open('temp.pdf', 'wb') as temp_file:
            temp_file.write(pdf_content)
        
        # Prepare the scan properties
        scan_properties = SubmissionProperties(
            sandbox=False,  # Set to False for production use
            #webhook_url="https://your-webhook-url.com"  # Optional: set up a webhook to receive results
        )
        
        # Submit the document for plagiarism check
        file_submission = FileDocument(
            file='temp.pdf',
            filename='document.pdf'
        )
        
        scan_id = Copyleaks.submit_file(auth, file_submission, scan_properties)
        
        # Note: Copyleaks processes the document asynchronously. 
        # You'll need to set up a webhook or poll for results.
        return f"Plagiarism check submitted. Scan ID: {scan_id}"
    
    
    except Exception as e:
        return f"Error in plagiarism check: {str(e)}"
    
    finally:
        # Clean up the temporary file
        import os
        if os.path.exists('temp.pdf'):
            os.remove('temp.pdf')


print(check_plagiarism_with_copyleaks(encode_pdf))'''
