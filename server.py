from itertools import chain
import time
from flask import Flask, request, jsonify, session
# from waitress import serve
from flask_cors import CORS
from firebase_config.user_handler import User
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
import pprint
from uuid import uuid4

from utils.chain_handler import ChainHandler
from utils.db_handler import DBHandler


app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

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
    file_objs = body["fileObjs"]
    file_details = body['fileDetails']
    user_id = body['userId']
    timestamp = body['dateCreated']


    rag_app = CombinedHandler(file_objs)    
    chain = rag_app.create_chain()
    # chain_id = "abc"
    chain_id = str(uuid4())
    pickle_file = f"chains/{chain_id}.pkl"
    
    with open(pickle_file, "wb") as f:
        pickle.dump(chain, f)

    chain_storage = ChainHandler(pickle_file, f'{chain_id}.pkl')
    chain_url = chain_storage.upload_chain()
    chain_storage.save_chain(user_id, chain_id, file_details, timestamp)
        
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
    question_obj = body["questionObj"]
    user_id = body["userId"]
    

    if not (chain_url and query):
        return {"error": "'query' or 'chainUrl' field is missing!"}
    try:
        chain = ChainHandler.download_chain(chain_url)
    except Exception as e:
        print(e)
        return {"error": "An error occured!"}

    result = CombinedHandler.process_query(query, chain)

    db = DBHandler()
    db.save_chat_question(question_obj)
    result = db.save_chat_response(result, user_id, chain_id)

    return jsonify(result)

def handle_signin():
    body = json.loads(request.data)
    user_id = body["userId"]
    date_created = body["dateCreated"]
    user = User(user_id, "uid", date_created)
    if user.exists():
        res = user.signin()
        return jsonify(res)
    return jsonify({"error": "Account does not exist!"})

def get_chain_obj():
    body = json.loads(request.data)
    user_id = body["userId"]
    chain_id = body["chainId"]

    result = ChainHandler.get_chain_obj(chain_id, user_id)
    return jsonify(result)

def get_chats():
    args = request.args
    user_id = args["userId"]
    chain_id = args["chainId"]

    db_handler = DBHandler()
    result = db_handler.get_chats(user_id, chain_id)

    return jsonify(result)

def get_uploads():
    body = json.loads(request.data)
    user_id = body.get("userId", False)
    if not user_id:
        return jsonify({"error": "userId is required"})
    
    db = DBHandler()
    result = db.fetch_uploads(user_id)

    return jsonify(result)

def delete_upload():
    body = json.loads(request.data)
    user_id = body.get("userId", False)
    chain_id = body.get("chainId", False)
    timestamp = body.get("dateDeleted", False)
    if not user_id:
        return jsonify({"error": "userId is required"})
    if not chain_id:
        return jsonify({"error": "chainId is required"})
    if not timestamp:
        return jsonify({"error": "timestamp is required"})

    db = DBHandler()
    res = db.delete_chain(user_id, chain_id, timestamp)

    return jsonify(res)
    

app.add_url_rule("/upload", "learn", learn, methods=["POST"])
app.add_url_rule("/query", "process_query", process_query, methods=["POST"])
app.add_url_rule("/signin", "handle_signin", handle_signin, methods=["POST"])
app.add_url_rule("/chain", "get_chain_obj", get_chain_obj, methods=["POST"])
app.add_url_rule("/chats", "get_chats", get_chats, methods=["GET"])
app.add_url_rule("/uploads", "get_uploads", get_uploads, methods=["POST"])
app.add_url_rule("/delete_upload", "delete_upload", delete_upload, methods=["POST"])
    

if __name__ == '__main__':
    app.run(debug=True)