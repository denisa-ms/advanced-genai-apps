In order to run these code samples you MUST have the following:

# Requirements
- Visual Studio Code
- Python (tested with 3.10, 3.12)
- Python virtual environment tool (venv)
- An Azure account 
- Azure subscription onboarded into Azure OpenAI
- Necessary permissions to deploy resources in the subscription

# Preparation

## Git repository
- Clone this repository to your local machine and open a terminal in the cloned directory.

## Visual Studio Code
- Windows
    - Install [Visual Studio Code](https://code.visualstudio.com/)
- Linux
    - Install [Visual Studio Code](https://code.visualstudio.com/)
- Mac
    - Install [Visual Studio Code](https://code.visualstudio.com/)

## Python
- Windows
    - Install [Python 3.12.2](https://www.python.org/downloads/release/python-3122/)
- Linux
    - It is usually pre-installed. Check version with `python3 --version`.
- Mac
    - `brew install python3`

### Python Virtual Environment Setup
-  To install virtualenv via pip run:
    - Windows / Mac / Linux:

         `pip3 install virtualenv`

- Creation of virtualenv (in the cloned Azure/AOAI-workshop directory):
    - Windows:

        `python -m virtualenv venv`
    - Mac / Linux:

        `virtualenv -p python3 venv`

- Activate the virtualenv:
    - Windows:

        `.\venv\Scripts\activate.ps1`
    - Mac / Linux

        `source ./venv/bin/activate`

### Install required libraries in your virtual environment
- Run the following command in the terminal:
    - Windows / Mac / Linux:

        `pip3 install -r requirements.txt`


# IMPORTANT!
## Setup environment variables
- Duplicate the `.env.template` file and rename the new file to `.env`.
- Open your new `.env` file and modify all the endpoints and api keys for all deployments as follows:
```
# This file contains the environment variables that are used by the application.

# AI studio demo credentials
AZURE_SEARCH_SERVICE_ENDPOINT="<your-search-service-endpoint>"
AZURE_SEARCH_ADMIN_KEY="<your-search-admin-key>"
AZURE_SEARCH_INDEX="product-info"
BLOB_CONNECTION_STRING="<your-blob-connection-string>"
BLOB_CONTAINER_NAME="product-data"

AZURE_SUBSCRIPTION_ID = "<your-azure-subscription-id>"
AZURE_AISTUDIO_PROJECT_RESOURCE_GROUP = "<your-azureaistudio-resource-group>"
AZURE_AISTUDIO_PROJECT_NAME = "<your-azureaistudio-project-name>"
AISTUDIO_AZURE_OPENAI_ENDPOINT="<your-openai-endpoint>"
AISTUDIO_AZURE_OPENAI_KEY="<your azure ai services key>"
AISTUDIO_OPENAI_GPT3516_DEPLOYMENT_NAME="gpt-35-turbo-16k"
AISTUDIO_OPENAI_GPT4_DEPLOYMENT_NAME="gpt-4"
AISTUDIO_AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-ada-002"
AISTUDIO_AZURE_OPENAI_EMBEDDING_MODEL_NAME="text-embedding-ada-002"
AISTUDIO_AZURE_OPENAI_EMBEDDING_DIMENSIONS=1536
# This field is only necessary if you want to use OCR to scan PDFs in the data source
AISTUDIO_AZURE_AI_SERVICES_KEY="<your azure ai services key>"

#Prompty requires the following environment variables to be set:
AZURE_OPENAI_ENDPOINT = "<your-openai-endpoint>"
AZURE_OPENAI_API_KEY = "<your-openai-key>"
OPENAI_API_VERSION = "2024-02-15-preview"
```