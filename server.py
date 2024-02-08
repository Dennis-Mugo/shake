from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from rags.pdf_handler import PDFHandler
from rags.text_handler import TextHandler
from rags.web_handler import WebHandler
from rags.word_handler import WordHandler
from rags.powerpoint_handler import PowerPointHandler

import json

from rags.yt_handler import YTHandler

app = Flask(__name__)
CORS(app, origins=["http://localhost"])

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)



@app.route("/", methods=["GET"])
def hello():
    # session["test"] = "This is a test"
    return jsonify({"result": "Welcome to Shake!"})

def learn():
    body = json.loads(request.data)
    file_type = body["file_type"]
    file_url = body["file_url"]
    if file_type == "pdf":
        rag_app = PDFHandler(file_url)
    elif file_type == "docx":
        rag_app = WordHandler(file_url)
    elif file_type == "pptx":
        rag_app = PowerPointHandler(file_url)
    elif file_type == 'txt':
        rag_app = TextHandler(file_url)
    elif file_type == "yt":
        rag_app = YTHandler(file_url)
    elif file_type == "web":
        rag_app = WebHandler(file_url)
        
    chain = rag_app.create_chain()
    session["rag_app"] = rag_app
    return jsonify({"result": "success"} if not chain else chain)

def process_query():
    body = json.loads(request.data)
    query = body["query"]

    rag_app = session.get("rag_app", False)
    if not rag_app:
        return {"Error": "No data trained"}
    result = rag_app.process_query(query)
    return jsonify(result)

app.add_url_rule("/upload", "learn", learn, methods=["POST"])
app.add_url_rule("/query", "process_query", process_query, methods=["POST"])
    

if __name__ == '__main__':
    app.run(debug=True)