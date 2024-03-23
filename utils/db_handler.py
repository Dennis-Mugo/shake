from uuid import uuid4 as v4
from utils.mongo_config import client
from time import time
import pprint

printer = pprint.PrettyPrinter()

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
    
    def get_chats(self, user_id, chain_id, secure=False):
        if secure:
            chats = self.chat_collection.find({"userId": user_id, "chainId": chain_id})
        else:
            chats = self.chat_collection.find({"chainId": chain_id})
        chats_list = [chat for chat in chats]
        print(chats_list[-1])

        return chats_list
    
    def get_last_chat(self, chain_id):
        # chat = self.chat_collection.find(
        #     {"chainId", chain_id}
        #     # sort=[( 'dateCreated', pymongo.DESCENDING )]
        #     ).limit(1)
        res = self.chat_collection.find({"chainId": chain_id, "role": "user"}).limit(1).sort({"$natural": -1})
        res = list(res)
        last_human_message = res[0] if len(res) else False

        res = self.chat_collection.find({"chainId": chain_id, "role": "assistant"}).limit(1).sort({"$natural": -1})
        res = list(res)
        last_assistant_message = res[0] if len(res) else False
        return {
            "assistant": last_assistant_message,
            "user": last_human_message
        }

        
    
    def fetch_uploads(self, user_id):
        # columns = {"_id": 1, "userId": 0, "chainId": 1, "dateCreated": 1, "files": 1}
        chains = self.chain_collection.find({"userId": user_id, "deleted": False}).sort({"$natural": -1})
        chains = [chain for chain in chains]

        return chains
    
        # Getting last chats disabled
        res = []
        for chain in chains:
            # printer.pprint(chain)
            obj = chain.copy()
            chat_obj = self.get_last_chat(obj["chainId"])
            obj["lastChat"] = chat_obj
            res.append(obj)

        return res
    
    def delete_chain(self, user_id, chain_id, timestamp):
        all_updates = {
            "$set": {"deleted": True, "dateDeleted": timestamp}
        }
        chain = self.chain_collection.find_one({"chainId": chain_id, "userId": user_id})
        if not chain:
            return {"showError": "Permission to delete document denied!"}
        
        self.chain_collection.update_one({"chainId": chain_id, "userId": user_id}, all_updates)
        return {"success": True}


