from flask import Flask, request, jsonify, session
# from waitress import serve
from flask_cors import CORS
from rags.combined_handler import CombinedHandler
# from flask_session import Session
from rags.pdf_handler import PDFHandler
from rags.text_handler import TextHandler
from rags.web_handler import WebHandler
from rags.word_handler import WordHandler
from rags.powerpoint_handler import PowerPointHandler
from rags.yt_handler import YTHandler

import json
import pickle
from uuid import uuid4

from utils.chain_handler import ChainHandler
import tests.mongo




app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "https://bizbanter.vercel.app"])

# app.config["SESSION_PERMANENT"] = True
# app.config['SESSION_TYPE'] = 'filesystem'
# Session(app)



@app.route("/", methods=["GET"])
def hello():
    # session["test"] = "This is a test"
    return jsonify({"result": "Welcome to Shake!"})

def learn():
    body = json.loads(request.data)
    # file_type = body["file_type"]
    file_objs = body["file_objs"]
    rag_app = CombinedHandler(file_objs)    
    chain = rag_app.create_chain()
    # chain_id = "abc"
    chain_id = str(uuid4())
    pickle_file = f"chains/{chain_id}.pkl"
    
    with open(pickle_file, "wb") as f:
        pickle.dump(chain, f)

    chain_storage = ChainHandler(pickle_file, f'{chain_id}.pkl')
    chain_url = chain_storage.upload_chain()
        
    result = {
        "result": "success",
        "chainId": chain_id,
        "chainUrl": chain_url
    }
    return jsonify(result)

def process_query():
    body = json.loads(request.data)
    query = body["query"]
    chain_id = body.get("chainId", False)
    chain_url = body.get("chainUrl", ChainHandler.url_from_id(chain_id))
    if not (chain_url and query):
        return {"Error": "'query' or 'chainUrl' field is missing!"}
    try:
        chain = ChainHandler.download_chain(chain_url)
    except:
        return {"Error": "An error occured!"}

    # if not rag_app_id:
    #     return {"Error": "chainId is required!"}
    # chain_path = f"chains/{rag_app_id}.pkl" 
    # with open(chain_path, "rb") as f:
    #     rag_app = pickle.load(f)
    

    # if not rag_app:
    #     return {"Error": "No data trained!"}
    
    # result = rag_app.process_query(query)
    result = CombinedHandler.process_query(query, chain)
    return jsonify(result)

app.add_url_rule("/upload", "learn", learn, methods=["POST"])
app.add_url_rule("/query", "process_query", process_query, methods=["POST"])
    

if __name__ == '__main__':
    app.run(debug=True)