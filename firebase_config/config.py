import firebase_admin
from firebase_admin import credentials, storage, firestore


cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'chatify--chat.appspot.com'})

bucket = storage.bucket()
db = firestore.client()