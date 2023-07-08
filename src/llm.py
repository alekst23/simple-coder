# llm.py
import os, traceback
import openai, asyncio
from config import OPENAI_API_KEY
import logging
import time

openai.api_key = OPENAI_API_KEY

C_DEFAULT_MODEL = "gpt-3.5-turbo-16k"
C_DEFAULT_TEMP = 0.8
C_DEFAULT_MAX_TOKENS = 8000
C_DEFAULT_MODEL_MAX_TOKENS = 16385 #4096

# Use openAI ChatGPT 3.5 Turbo chat completion end point
async def generate_chat_completion(message_log, model_name=C_DEFAULT_MODEL, max_tokens=C_DEFAULT_MAX_TOKENS, temp=C_DEFAULT_TEMP):
    while True:
        try:
            assert isinstance(message_log, list), "message log must be a list"
            assert len(message_log) > 0, "message log must not be empty"

            response = await openai.ChatCompletion.acreate(
                model=model_name,
                messages=message_log,
                temperature=temp,
                max_tokens=max_tokens
            )
            response = response.choices[0]['message']['content']
            break
        except openai.error.RateLimitError:
            logging.info("(generate_chat_completion) Rate limit exceeded, retrying...")
            time.sleep(5)
            continue
        except openai.error.ServiceUnavailableError:
            logging.info("(generate_chat_completion) ServiceUnavailableError, retrying...")
            time.sleep(5)
            continue
        except AssertionError as e:
            logging.error("(generate_chat_completion) " + str(e))
            return None
        except openai.error.APIConnectionError:
            logging.info("(count_message_tokens) APIConnectionError, retrying...")
            # sleep for N seconds
            time.sleep(10)
            continue
        except Exception as e:
            print(traceback.format_exc())
            logging.error("(generate_chat_completion) " + str(e))
            raise e

    return response


async def count_message_tokens(message_log):
    while True:
        try:
            response = openai.ChatCompletion.create(
                model=C_DEFAULT_MODEL,
                messages=message_log,
                temperature=0.0,
                max_tokens=1
            )
            response = response["usage"]["prompt_tokens"]
            break
        except openai.error.RateLimitError:
            logging.info("(count_message_tokens) Rate limit exceeded, retrying...")
            await asyncio.sleep(5)
            continue
        except openai.error.APIConnectionError:
            logging.info("(count_message_tokens) APIConnectionError, retrying...")
            # sleep for N seconds
            await time.sleep(10)
            continue
        
    return response