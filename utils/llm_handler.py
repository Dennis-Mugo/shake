from dotenv import load_dotenv
from langchain.llms import GooglePalm
from langchain.chat_models import ChatOpenAI
from langchain.llms import HuggingFaceHub
from langchain.llms import VertexAI


import os

load_dotenv()

class LLMHandler:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")

    
    def get_llm(self):
        self.llm = self.open_ai_llm()
        return self.llm
    
    def huggingface_llm(self):
        llm = HuggingFaceHub(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            huggingfacehub_api_token=self.huggingface_api_key,
            model_kwargs={
                "temperature":0.7,
                # "top_p": 0.5,
                # "do_sample": True,
                "max_new_tokens":1024
            })
        return llm
    
    def open_ai_llm(self):
        llm = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            model_name="gpt-3.5-turbo",
            temperature=0.9,
            max_tokens=500,
        )
        return llm

    def google_llm(self):
        llm = GooglePalm(model_name="models/gemini-pro")
        return llm
        