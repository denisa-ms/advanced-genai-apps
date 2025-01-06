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



def define_agents():
    llm_config = {
        "cache_seed": 43,  # change the cache_seed for different trials
        "temperature": 0,
        "timeout": 120,  # in seconds
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

    user_proxy = autogen.UserProxyAgent(
        name="Admin",
        system_message="A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved "
                    "by this admin.",
        code_execution_config={
            "work_dir": "code",
            "use_docker": False
        },
        human_input_mode="TERMINATE",
    )
    engineer = autogen.AssistantAgent(
        name="Engineer",
        llm_config=llm_config,
        system_message="""Engineer. You follow an approved plan. Make sure you save code to disk.  You write python/shell 
        code to solve tasks. Wrap the code in a code block that specifies the script type and the name of the file to 
        save to disk.""",
    )
    scientist = autogen.AssistantAgent(
        name="Scientist",
        llm_config=llm_config,
        system_message="""Scientist. You follow an approved plan. You are able to categorize papers after seeing their 
        abstracts printed. You don't write code.""",
    )
    planner = autogen.AssistantAgent(
        name="Planner",
        system_message="""Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
    The plan may involve an engineer who can write code and a scientist who doesn't write code.
    Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a scientist.
    """,
        llm_config=llm_config,
    )

    critic = autogen.AssistantAgent(
        name="Critic",
        system_message="Critic. Double check plan, claims, code from other agents and provide feedback. Check whether the "
                    "plan includes adding verifiable info such as source URL.",
        llm_config=llm_config,
    )
    group_chat = autogen.GroupChat(
        agents=[user_proxy, engineer, scientist, planner, critic], messages=[], max_round=12
    )
    manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config)
    return user_proxy, engineer, scientist, planner, critic, manager


user_proxy, engineer, scientist, planner, critic, manager = define_agents()
user_proxy.initiate_chat(
    manager,
    message="""
        Find papers on LLM applications from arxiv in the last week, create a markdown table of different domains.
    """,
)