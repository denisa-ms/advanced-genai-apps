import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents.models import VectorizedQuery
from tenacity import retry, wait_random_exponential, stop_after_attempt
from openai import AzureOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    SearchField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch,
    SearchIndex,
    AzureOpenAIVectorizer,
    AzureOpenAIParameters
)
import yaml


class RAG:
    def __init__(self) -> None:
        load_dotenv()
        # Configure environment variables
        self.service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
        self.key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
        self.index_name = os.getenv("AZURE_SEARCH_INDEX")

        self.AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
        self.AZURE_OPENAI_GPT4_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_GPT4_DEPLOYMENT_NAME")
        self.AZURE_OPENAI_EMBEDDINGS_ADA_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDINGS_ADA_DEPLOYMENT_NAME")
        self.AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
        
        self.aoai_client = AzureOpenAI(
            azure_endpoint = self.AZURE_OPENAI_ENDPOINT, 
            api_key=self.AZURE_OPENAI_API_KEY,  
            api_version=self.AZURE_OPENAI_API_VERSION
        )

        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=self.AZURE_OPENAI_EMBEDDINGS_ADA_DEPLOYMENT_NAME,
            azure_endpoint=self.AZURE_OPENAI_ENDPOINT,
            openai_api_version=self.AZURE_OPENAI_API_VERSION,
            api_key=self.AZURE_OPENAI_API_KEY
        )
        
        credential = AzureKeyCredential(self.key)
        self.aisearch = SearchIndexClient(endpoint=self.service_endpoint, credential=credential)
            
    def __call__(self,question: str = " ") -> str:
        """>>>RAG Flow entry function."""
        response = self.chat(question)
        return response

    def call_openAI(self, question, answers):
        grounded_prompt="""
            You are a friendly assistant answering users questions.
            Answer the query using only the answers provided below in a friendly and concise bulleted manner.
            Answer ONLY with the facts listed in the list of answers below.
            If there isn't enough information below, say you don't know.
            Do not generate answers that don't use the answers below.
            Query: {question}
            Sources:\n{answers}
        """
        messages=[
            {
                "role": "user",
                "content": grounded_prompt.format(question=question, answers=answers)
            }
        ]
        response = self.aoai_client.chat.completions.create(
            model=self.AZURE_OPENAI_GPT4_DEPLOYMENT_NAME,
            messages = messages,
            temperature=0.7,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )
        return response.choices[0].message.content

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def calc_embeddings(self, text):
        # model = "deployment_name"
        embeddings = self.aoai_client.embeddings.create(input = [text], model=self.AZURE_OPENAI_EMBEDDINGS_ADA_DEPLOYMENT_NAME).data[0].embedding
        return embeddings

    def do_search(self, query):
        fields = "embedding"
        embedding = self.calc_embeddings(query)
        vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=3, fields=fields)

        print("$$$$" + str(type(self.aisearch)))
        results = self.aisearch.search(  
            search_text=None,  
            vector_queries= [vector_query],
            select=["content"],
        )  
        answer = ''
        for result in results:  
            print(f"Score: {result['@search.score']}")  
            print(f"Content: {result['content']}")  
            answer = answer + result['content']
        return answer

    def chat(self, question, **kwargs):
        answers = self.do_search(question)
        response = self.call_openAI(question, answers)
        return response

 
if __name__ == "__main__":
        print("rag_main.py") 
        rag = RAG()
        
   