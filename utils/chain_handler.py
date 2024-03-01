from firebase_config.config import bucket
import os
import cloudpickle as cp
from urllib.request import urlopen
from dotenv import load_dotenv

load_dotenv()

class ChainHandler:
    def __init__(self, chain_path, chain_name):
        self.chain_path = chain_path
        self.chain_name = chain_name
        

    def upload_chain(self, storage_path="bizbanter_chains"):
        print("Uploading chain...")
        blob = bucket.blob(f'{storage_path}/{self.chain_name}')
        blob.upload_from_filename(self.chain_path)
        blob.make_public()
        self.url = blob.public_url
        print(self.url)
        if os.path.exists(self.chain_path):
            os.remove(self.chain_path)
        return self.url
    
    @staticmethod
    def url_from_id(chain_id):
        if not chain_id:
            return False
        url = f'https://storage.googleapis.com/chatify--chat.appspot.com/bizbanter_chains/{chain_id}.pkl'
        return url
    
    @staticmethod
    def download_chain(url):
        chain = cp.load(urlopen(url))
        return chain