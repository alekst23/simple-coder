# Configuration settings for the Discord chatbot

import dotenv,  os

dotenv.load_dotenv('.env')

# OpenAI API Key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Other configurations can be added here as needed