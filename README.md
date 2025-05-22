# Neural Integrated Desktop Assistant (NIDA-UNIX)

## Introduction
NIDA-UNIX is a smart desktop assistant built for developers. Just tell it what you want to do in plain English, and it takes care of the rest—automatically running the right system commands for you. It even handles things like sudo access and follow-up prompts. With NIDA-UNIX, you get a full desktop environment that makes complex tasks easier and boosts your productivity.

## Features 
1. Automated Command Execution: Executes system commands without the need to type them every time.
2. Describe any task in plain English, and NIDA-UNIX will automatically generate and execute the required system commands step by step.
3. Sudo(Admin) Access Handling: It can run commands that need special permissions (like using sudo) and handle any follow-up prompts.
4. Database Creation – It can create database automatically using our model. Also can automate database-related tasks as needed.
5. Activity Logging – Maintains a comprehensive log history of executed actions. It saves a history of everything it does, so you can check what happened later.
6. AI Integration – Works with powerful AI tools like GROQ and OLLAMA (supports LLaMA2, Code LLaMA, Mistral, and Gemma-2B) to help you with smart automation.


## System Architecture
![alt text](<System Architecture.jpg>)

## Upcoming Features 
1. Enable voice-based input functionality using predefined model (21 May)
2. Integrate stable fine-tuned model into the application for response generation (31 May)
3. Enhance System Architecture with Validation Layers (27 May)
4. Develop custom Indian Accent Speech Recognition Model (31 May)
5. Provide Executable Application for Unix-Based Systems (22 May)
6. Integrate external services (28 May)


## Prerequisites
1. A Unix-based operating system

2. Python 3 (version ≥ 3.10.12)

## Preferred Environment
1. Python 3.10.12 (recommended for best compatibility)


## Steps to setup project :

1. Clone the Repository. 
``` 
git clone git@github.com:NIDA-DEVS/NIDA-UNIX.git 
cd NIDA-UNIX
```

2. Create a virtual environment and activate it
```
python -m venv venv
source venv/bin/activate
```

3. Install Dependencies
```
pip install -r requirements.txt
```          
4. Get your LangSmith api key here 
https://docs.smith.langchain.com/administration/how_to_guides/organization_management/create_account_api_key

5. Create a <b>.env</b> File
In the root directory of the project and add your LangChain API key:
``` 
LANGCHAIN_API_KEY = "api-key"
```
6. Configure the API Key </br>
Open <b>core/nodes_graph.py</b> and assign your LangChain API key to the appropriate variable.
```
os.environ["LANGCHAIN_API_KEY"] = os.getenv["LANGCHAIN_API_KEY"]
```

7. Run the project using command python run main.py 
``` 
python main.py
```

8. After running app iff using Groq service provider, you will need Groq api key
* Login or signup on groq website: <br>
https://console.groq.com/keys
* After signingup click on create api key and give it some name 
* copy api key and paste on Groq api key section while using it, look in image for reference : <br>
![alt text](<groq api interface image.png>) <br>

<hr>
<b>Note : </b> Currently there are limited features for Windows, we are working on windows features and will update soon.  