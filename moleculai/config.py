# Configuration settings for the Discord chatbot

import dotenv,  os

if not os.path.exists('.env'): raise Exception(".env file not found")

dotenv.load_dotenv('.env')

# OpenAI API Key
if apikey := os.environ.get("OPENAI_API_KEY"): 
    OPENAI_API_KEY = apikey
else:
    raise Exception("OPENAI_API_KEY is not set in .env file")


# Other configurations can be added here as needed