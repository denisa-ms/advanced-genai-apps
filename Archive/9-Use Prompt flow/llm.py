import os
from dotenv import load_dotenv
from openai import OpenAI
from promptflow.tracing import trace
from openai import AzureOpenAI

load_dotenv()
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_GPT4_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_GPT4_DEPLOYMENT_NAME")
AZURE_OPENAI_EMBEDDINGS_ADA_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDINGS_ADA_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
azure_openai_embedding_dimensions = 1536

def get_client():
    aoai_client = AzureOpenAI(
        azure_endpoint = AZURE_OPENAI_ENDPOINT, 
        api_key=AZURE_OPENAI_API_KEY,  
        api_version=AZURE_OPENAI_API_VERSION
    )
    return aoai_client

# for AOAI, deployment name is customized by user, not model name.
@trace
def my_llm_tool(prompt: str,deployment_name: str,max_tokens: int = 120,temperature: float = 1.0,top_p: float = 1.0,n: int = 1,) -> str:
    messages = [{"content": prompt, "role": "system"}]
    response = get_client().chat.completions.create(
        messages=messages,
        model=deployment_name,
        max_tokens=int(max_tokens),
        temperature=float(temperature),
        top_p=float(top_p),
        n=int(n),
    )

    # get first element because prompt is single.
    return response.choices[0].message.content


if __name__ == "__main__":
    result = my_llm_tool(
        prompt="Write a simple Hello, world! program that displays the greeting message.",
        deployment_name="gpt-4o",
    )
    print(result)
