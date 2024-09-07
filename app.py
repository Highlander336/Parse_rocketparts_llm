# app.py
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import sqlite3
import json
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
import logging
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate  # Add this import
import re

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database setup
conn = sqlite3.connect('rocket_specs.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS parts
             (id INTEGER PRIMARY KEY, name TEXT, description TEXT)''')
conn.commit()
conn.close()

# Set up Anthropic API key
os.environ["ANTHROPIC_API_KEY"] = "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"

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_pdf(filepath):
    try:
        # Load PDF
        loader = PyPDFLoader(filepath)
        documents = loader.load()

        # Split documents
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)

        # Create embeddings and vector store
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        docsearch = FAISS.from_documents(texts, embeddings)

        # Create QA chain with Claude
        llm = ChatAnthropic(model="claude-2.1", temperature=0)  # Changed from "claude-2" to "claude-2.1"
        
        # Custom prompt
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="Given the following context about a rocket or spacecraft:\n\n{context}\n\nPlease extract and list all parts mentioned along with a brief description for each. Format the response as a JSON object with 'name' and 'description' fields for each part. Question: {question}"
        )
        
        qa = RetrievalQA.from_chain_type(
            llm=llm, 
            chain_type="stuff", 
            retriever=docsearch.as_retriever(),
            chain_type_kwargs={"prompt": prompt}
        )

        # Query for parts
        query = "What are the parts of the rocket or spacecraft described in this document, and what are their characteristics?"
        result = qa.invoke({"query": query})

        # Extract JSON from the result
        json_match = re.search(r'\{.*\}', result['result'], re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json_str
        else:
            raise ValueError("No JSON object found in the LLM output")

    except Exception as e:
        logger.error(f"Error in process_pdf: {str(e)}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html', error='No file part')
    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', error='No selected file')
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process PDF and extract parts information
            parts_info = process_pdf(filepath)
            logger.debug(f"LLM output: {parts_info}")
            
            # Parse the JSON string returned by the LLM
            parts_dict = json.loads(parts_info)
            
            # Store parts information in the database
            conn = sqlite3.connect('rocket_specs.db')
            c = conn.cursor()
            for name, details in parts_dict.items():
                c.execute('INSERT INTO parts (name, description) VALUES (?, ?)', 
                          (name, details['description']))
            conn.commit()
            conn.close()
            
            # Render the index template with results
            return render_template('index.html', parts=parts_dict)
        except ValueError as e:
            logger.error(f"LLM output processing error: {str(e)}")
            return render_template('index.html', error='Failed to extract parts information from the document')
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return render_template('index.html', error='Failed to parse LLM output as JSON')
        except Exception as e:
            logger.error(f"Unexpected error in upload_file: {str(e)}")
            return render_template('index.html', error=str(e))
    return render_template('index.html', error='File type not allowed')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    conn = sqlite3.connect('rocket_specs.db')
    c = conn.cursor()
    c.execute("SELECT * FROM parts WHERE name LIKE ? OR description LIKE ?", 
              ('%'+query+'%', '%'+query+'%'))
    results = c.fetchall()
    conn.close()
    return jsonify([{'id': r[0], 'name': r[1], 'description': r[2]} for r in results])

if __name__ == '__main__':
    app.run(debug=True)
