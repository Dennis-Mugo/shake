from langchain.embeddings import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings



class EmbeddingsHandler:
    def get_embeddings_model(self):
        self.embeddings = self.get_openai_embeddings()
        return self.embeddings
    
    def get_google_embeddings(self):
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    def get_openai_embeddings(self):
        return OpenAIEmbeddings();
    