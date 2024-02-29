import pickle
import requests
import cloudpickle as cp

url = "https://storage.googleapis.com/chatify--chat.appspot.com/bizbanter_chains/abc.pkl"
response = requests.get(url)
print(type(response.content))
with open("", "bx") as f:
    chain = pickle.load(f)