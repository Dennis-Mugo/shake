from dotenv import load_dotenv
import pprint
import os
from pymongo import MongoClient


load_dotenv()

mongo_pass = os.getenv("MONGO_PASS")
connection_uri = f"mongodb+srv://dennis:{mongo_pass}@cluster1.ozfksqb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"



client = MongoClient(connection_uri)

print(client.list_database_names())
banter_db = client.banter
collections = banter_db.list_collection_names()
print(collections)

def insert_doc():
    user_colletion = banter_db.test_users
    obj = {
        "name": "Dennis",
        "type": "me"
    }
    res = user_colletion.insert_one(obj)
    print(res.inserted_id)

person_collection = banter_db.people #Create new collection
def create_documents():
    first_names = ["Hawi", "Maryanne", "Michael", "Eugene", "Salim", "Philip"]
    last_names = ["Bedada", "Kariuki", "Gacho", "Clinton", "Iddi", "Osoro"]
    ages = [31, 32, 33, 34, 35]

    docs = []
    for first_name, last_name, age in zip(first_names, last_names, ages):
        docs.append({
            "first_name": first_name,
            "last_name": last_name,
            "age": age
        })
    person_collection.insert_many(docs)


printer = pprint.PrettyPrinter()

def find_all_people():
    people = person_collection.find()
    for person in people:
        printer.pprint(person)

def find_witta():
    person = person_collection.find_one({"first_name": "Hawi", "last_name": "Bedada"})
    printer.pprint(person)

def count_all_people():
    count = person_collection.count_documents(filter={})
    print("Number of people", count)

def get_person_by_id(person_id):
    from bson.objectid import ObjectId

    _id = ObjectId(person_id)
    person = person_collection.find_one({"_id": _id})
    printer.pprint(person)


def get_age_range(min_age, max_age):
    query = {
        "$and": [
            {"age": {"$gte": min_age}},
            {"age": {"$lte": max_age}}
        ]
    }
    people = person_collection.find(query).sort("age")
    for person in people:
        printer.pprint(person)
    
def project_columns():
    columns = {"_id": 0, "first_name": 1, "last_name": 1}
    people = person_collection.find({}, columns)
    for person in people:
        printer.pprint(person)

def update_person_by_id(person_id):
    from bson.objectid import ObjectId

    _id = ObjectId(person_id)
    all_updates = {
        "$set": {"new_field": True},
        "$inc": {"age": 1},
        "$rename": {"first_name": "first", "last_name": "last"}
    }

    person_collection.update_one({"_id": _id}, all_updates)
    #To remove a key
    person_collection.update_one({"_id": _id}, {"$unset": {"new_field": ""}})


def replace_doc(person_id):
    from bson.objectid import ObjectId
    _id = ObjectId(person_id)
    new_doc = {
        "first_name": "not Michael",
        "last_name": "not Gacho",
        "age": 230
    }
    person_collection.replace_one({"_id": _id}, new_doc)

def delete_doc_by_id(person_id):
    from bson.objectid import ObjectId
    _id = ObjectId(person_id)

    person_collection.delete_one({"_id": _id})

#65e1b8deb51a72d5949aee25
delete_doc_by_id("65e1b8deb51a72d5949aee25")

