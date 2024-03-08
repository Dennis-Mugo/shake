
from firebase_config.config import auth
from utils.mongo_config import client

class User():
    def __init__(self, value, identifier, timestamp):
        self.identifier = identifier
        self.value = value
        self.timestamp = timestamp

    def exists(self):
        return self.get_details()

    def get_details(self):
        try:
            if self.identifier == 'email':
                self.email = self.value
                obj = auth.get_user_by_email(self.email)
                self.uid = obj.uid
            elif self.identifier == "uid":
                self.uid = self.value
                obj = auth.get_user(self.uid)
                self.email = obj.email
        except:
            return False
        self.display_name = obj.display_name
        self.photo_url = obj.photo_url
        self.provider_id = obj.provider_id
        return True
    
    def signin(self):
        user_collection = client.banter.users
        db_user = user_collection.find_one({"userId": self.uid})
        if db_user:
            user_collection.update_one({"userId": self.uid}, {"$set": {"lastLogin": self.timestamp}})
            updated_user = user_collection.find_one({"userId": self.uid})
            return {"message": "successful signin", "user": updated_user}
        else:
            obj = {
                "userId": self.uid,
                "_id": self.uid,
                "email": self.email,
                "displayName": self.display_name,
                "photoUrl": self.photo_url,
                "dateCreated": self.timestamp,
                "lastLogin": self.timestamp
            }
            user_collection.insert_one(obj)
            return {"message": "successful signup", "user": obj}
    
