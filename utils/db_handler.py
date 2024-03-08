from uuid import uuid4 as v4
from utils.mongo_config import client
from time import time

class DBHandler():
    def __init__(self):
        self.user_collection = client.banter.users
        self.chain_collection = client.banter.chains
        self.chat_collection = client.banter.chats

    def save_chat_question(self, question_obj):
        question_obj['_id'] = question_obj["chatId"]
        self.chat_collection.insert_one(question_obj)

    def save_chat_response(self, chain_result, user_id, chain_id):
        now = str(int(time()) * 1000)
        chat_id = str(v4())
        obj = {
            "content": chain_result["answer"],
            "chainId": chain_id,
            "userId": user_id,
            "role": "assistant",
            "sourceDocuments": chain_result["sourceDocuments"],
            "chatId": chat_id,
            "dateCreated": now,
            "_id": chat_id 
        }
        self.chat_collection.insert_one(obj)
        return obj