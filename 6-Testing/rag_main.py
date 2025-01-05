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

load_dotenv()
# Configure environment variables
service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
index_name = os.getenv("AZURE_SEARCH_INDEX")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_GPT4_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_GPT4_DEPLOYMENT_NAME")
AZURE_OPENAI_EMBEDDINGS_ADA_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDINGS_ADA_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
azure_openai_embedding_dimensions = 1536

# load agent configuration (variant) from the YAML file
def load_agent_configuration(agent_folder: str, agent_config_file: str) -> dict:

    # add check for input arguments
    if not agent_folder or not agent_config_file:
        raise ValueError("Agent folder and agent config file are required.")

    # Get the directory of the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Construct the absolute path to the configuration file
    config_path = os.path.join(project_root, agent_folder, agent_config_file)

    # Load the configuration file
    with open(config_path, 'r') as file:
        try:
            # Parse the YAML content
            config_data = yaml.safe_load(file)
            # Output the resulting dictionary
            # print(config_data)
        except yaml.YAMLError as error:
            print(f"Error parsing agent config YAML file: {error}")
            raise error

    return config_data

class RAG:
    def __init__(self) -> None:
        self.aoai_client = AzureOpenAI(
            azure_endpoint = AZURE_OPENAI_ENDPOINT, 
            api_key=AZURE_OPENAI_API_KEY,  
            api_version=AZURE_OPENAI_API_VERSION
        )

        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=AZURE_OPENAI_EMBEDDINGS_ADA_DEPLOYMENT_NAME,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            openai_api_version=AZURE_OPENAI_API_VERSION,
            api_key=AZURE_OPENAI_API_KEY
        )
        
        credential = AzureKeyCredential(key)
        self.aisearch = SearchIndexClient(endpoint=service_endpoint, credential=credential)
            
        self.rag_config = load_agent_configuration("./7-Testing/", "rag_agent_config.yaml")            
          


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
            model=AZURE_OPENAI_GPT4_DEPLOYMENT_NAME,
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
    # Function to generate embeddings for title and content fields, also used for query embeddings
    def calc_embeddings(self, text):
        # model = "deployment_name"
        embeddings = self.aoai_client.embeddings.create(input = [text], model=AZURE_OPENAI_EMBEDDINGS_ADA_DEPLOYMENT_NAME).data[0].embedding
        return embeddings

    def do_search(self, query):
        fields = "embedding"
        embedding = self.calc_embeddings(query)
        vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=3, fields=fields)
    
        results = self.search_client.search(  
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

    def chat(self, session_id, question, **kwargs):
        answers = self.do_search(question)
        response = self.call_openAI(question, answers)
        return response

 
if __name__ == "__main__":
        print("rag_main.py") 
        rag = RAG()
        
   