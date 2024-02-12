import os
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from uuid import uuid4
import requests

from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import AstraDB as LangAstraDB
from astrapy.db import AstraDB
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

class TextHandler():
    def __init__(self, file_url):
        self.file_url = file_url
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    def load_llm(self):
        print("Loading llm")
        self.llm = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            model_name="gpt-3.5-turbo",
            temperature=0.9,
            max_tokens=500,
        )

    def load_data(self):
        print("Loading data")
        response = requests.get(self.file_url)
        file_name = str(uuid4()) + ".txt"
        with open(file_name, 'wb') as f:
            f.write(response.content)
        loader = TextLoader(file_name)
        self.data = loader.load()
        if os.path.exists(file_name):
            os.remove(file_name)
        # print("data length", len(data))

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
        embeddings = OpenAIEmbeddings()

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

    def process_query(self, query):
        result = self.chain(query)
        # print(result)
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