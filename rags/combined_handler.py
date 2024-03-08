import os
from langchain.chat_models import ChatOpenAI
from langchain.llms import GooglePalm
from dotenv import load_dotenv
from uuid import uuid4
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_google_genai import GoogleGenerativeAI
import requests

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
# from langchain_community.vectorstores import AstraDB as LangAstraDB
from astrapy.db import AstraDB
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.llms import HuggingFaceHub
from rags.pdf_handler import PDFHandler
from rags.web_handler import WebHandler
from rags.word_handler import WordHandler
from rags.yt_handler import YTHandler

from utils.embeddings_handler import EmbeddingsHandler
from utils.llm_handler import LLMHandler


from langchain.document_loaders import OnlinePDFLoader

load_dotenv()

class CombinedHandler():
    def __init__(self, file_objs):
        self.file_objs = file_objs
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")

    def load_llm(self):
        print("Loading llm")
        llm_loader = LLMHandler()
        self.llm = llm_loader.get_llm()
        # self.llm = ChatOpenAI(
        #     openai_api_key=self.openai_api_key,
        #     model_name="gpt-3.5-turbo",
        #     temperature=0.9,
        #     max_tokens=500,
        # )
        # self.llm = GooglePalm(temperature=0.8)
        # self.llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=self.google_api_key, temperature=0.2,convert_system_message_to_human=True)
        
        # print(type(self.llm))

    def sort_files(self):
        # web, pdf, yt, docx
        types = ["web", "pdf", "yt", "docx"]

        # res = {type: [] for type in types}
        res = []
        for obj in self.file_objs:
            file_type = obj.get("file_type")
            if file_type == "pdf":
                handler = PDFHandler(obj["file_urls"])
                # res["pdf"].append(handler)
                res.append(handler)
            elif file_type == "docx":
                handler = WordHandler(obj["file_urls"])
                # res["docx"].append(handler)
                res.append(handler)
            elif file_type == 'web':
                handler = WebHandler(obj["file_urls"])
                # res['web'].append(handler)
                res.append(handler)
            elif file_type == 'yt':
                handler = YTHandler(obj["file_urls"])
                # res['yt'].append(handler)
                res.append(handler)
        return res


    def load_data(self):
        print("Loading data")
        sorted_handlers = self.sort_files()
        self.data = []
        for handler in sorted_handlers:
            data = handler.load_data()
            self.data += data
        print("data length", len(self.data))

    def split_data(self):
        print("Splitting data")
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " "],
            chunk_size=500,
            chunk_overlap=150,
            length_function=len
        )
        self.chunks = splitter.split_documents(self.data)
        print("No of chunks:", len(self.chunks))

    def embed_data(self):
        print("Embedding data")
        embeddings_loader = EmbeddingsHandler()
        embeddings = embeddings_loader.get_embeddings_model()
        # embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        # embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)

        # ASTRA DB stuff
        # db_token = os.getenv("ASTRADB_TOKEN")
        # db_endpoint = "https://945c811b-2d65-4b85-83ec-cc5b1649c4c1-us-east1.apps.astra.datastax.com"
        # collection_name = "b" + str(uuid4()).replace("-", "_")
        # print(collection_name)
        # vector_store = LangAstraDB(
        #     embedding=embeddings,
        #     collection_name=collection_name,
        #     api_endpoint=db_endpoint,
        #     token=db_token,
        # )
        # inserted_ids = vector_store.add_documents(self.chunks)

        vector_store = FAISS.from_documents(documents=self.chunks, embedding=embeddings)
        self.retriever = vector_store.as_retriever()
        self.vector_store = vector_store
        print("Vector store created")
        
    def get_chain(self):
        print("Creating chain")
        prompt_template = """Given the following context and a question, generate an answer based on this context only.
        In the answer try to provide as much text as possible from "context" section in the source document context. The response should be as clear and detailed.
        The answer should not start with the word response.
        The answer should be in simple-to-understand language.
        If the answer is not found in the context, kindly state "Sorry, I cannot provide a response from the context provided." Don't try to make up an answer.

        CONTEXT: {context}

        QUESTION: {question}"""


        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        chain_type_kwargs = {"prompt": PROMPT}

        
        
        self.chain = RetrievalQA.from_chain_type(llm=self.llm,
                                    chain_type="stuff",
                                    retriever=self.retriever,
                                    input_key="query",
                                    return_source_documents=True,
                                    chain_type_kwargs=chain_type_kwargs
                                    )
        
        
    @staticmethod
    def process_query(query, chain):
        # result = self.chain(query)
        result = chain(query)
        source_docs = result["source_documents"]
        formated_source_docs = []
        for doc in source_docs:
            obj = {}
            obj["pageContent"] = doc.page_content
            obj["metadata"] = doc.metadata
            formated_source_docs.append(obj)
        return {"answer": result["result"], "sourceDocuments": formated_source_docs}

    def create_chain(self):
        self.load_llm()
        self.load_data()
        self.split_data()
        self.embed_data()
        self.get_chain()
        return self.chain