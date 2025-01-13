import autogen
import os
from dotenv import load_dotenv
import os

load_dotenv()
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_GPT4o_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_GPT4o_DEPLOYMENT_NAME")
AZURE_OPENAI_EMBEDDINGS_ADA_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDINGS_ADA_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")


def main():

    llm_config = {
        "config_list": 
        [
            {
                "model": AZURE_OPENAI_GPT4o_DEPLOYMENT_NAME,
                "api_type": "azure",
                "api_key": AZURE_OPENAI_API_KEY,
                "base_url": AZURE_OPENAI_ENDPOINT,
                "api_version": AZURE_OPENAI_API_VERSION
            }
        ]
    }

    assistant = autogen.AssistantAgent(
        name="Assistant",
        llm_config=llm_config
    )

    user_proxy = autogen.UserProxyAgent(
        name="user",
        human_input_mode="ALWAYS",
        code_execution_config={
            "work_dir": "coding",
            "use_docker": False
        }
    )

    user_proxy.initiate_chat(assistant, message="Plot a chart of META and TESLA stock price change.", max_turns=10)


if __name__ == "__main__":
    main()