# Neural Integrated Desktop Assistant (NIDA-UNIX)

## Introduction
NIDA-UNIX is a powerful automation project designed specifically for developers. It provides seamless access to a full desktop environment and allows the execution of system commands directly, simplifying complex workflows and enhancing productivity. Developer just need to tell NIDA-UNIX about what to do and it can automatically perform task.

## Features 
1. Automated Command Execution: Executes system commands without the need to type them every time.
2. Sudo(Admin) Access Handling: It can run commands that need special permissions (like using sudo) and handle any follow-up prompts.
3. Database Creation – It can create database automatically using our model. Also can automate database-related tasks as needed.
4. Activity Logging – Maintains a comprehensive log history of executed actions. It saves a history of everything it does, so you can check what happened later.
5. AI Integration – Works with powerful AI tools like GROQ and OLLAMA (supports LLaMA2, Code LLaMA, Mistral, and Gemma-2B) to help you with smart automation.


## Demo Video


## System Architecture
![alt text](<System Architecture.jpg>)

## Upcoming Features 
1. Enable voice-based input functionality using predefined model (17 May)
2. Integrate stable fine-tuned model into the application for response generation (7 June)
3. Enhance System Architecture with Validation Layers (24 May)
4. Develop custom Indian Accent Speech Recognition Model (10 June)
5. Provide Executable Application for Unix-Based Systems (21 May)
6. Integrate external services (31 May)


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

* for Linux or Mac :
```
python -m venv venv
source venv/bin/activate
```
* for Windows :
```
python -m venv venv
.\venv\Scripts\Activate.ps1 
```

3. Install Dependencies
```
pip install -r requirements.txt
```          
4. Get your LangSmith api key here 
https://docs.smith.langchain.com/administration/how_to_guides/organization_management/create_account_api_key

4. Create a <b>.env</b> File
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
* copy api key and paste on Groq api key section while using it, look in image for reference :
![alt text](<groq api interface image.png>)