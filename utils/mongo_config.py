from dotenv import load_dotenv
import os
import pymongo

load_dotenv()

mongo_pass = os.getenv("MONGO_PASS")
connection_uri = f"mongodb+srv://dennis:{mongo_pass}@cluster1.ozfksqb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"


client = pymongo.MongoClient(connection_uri)