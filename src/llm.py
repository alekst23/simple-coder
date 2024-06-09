# llm.py
import traceback
import openai
import logging
import math
import asyncio

from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

C_DEFAULT_MODEL_CODE = "35"

C_MODELS = {
    "35":{
        "model_name": "gpt-3.5-turbo-1106",
        "max_tokens": 16385
    },
    "40":{
        "model_name": "gpt-4-1106-preview",
        "max_tokens": 36000
    }
}

C_DEFAULT_TEMP = 1.0
C_DEFAULT_COMPLETION_TOKENS = 4096


async def generic_retry_handler(func, *args, **kwargs):
    while True:
        try:
            return await func(*args, **kwargs)
        except openai.RateLimitError:
            logging.info("(count_message_tokens) Rate limit exceeded, retrying...")
            await asyncio.sleep(5)
        except openai.APIConnectionError:
            logging.info("(count_message_tokens) APIConnectionError, retrying...")
            await asyncio.sleep(10)
        except Exception as e:
            print(traceback.format_exc())
            logging.error("(count_message_tokens) " + str(e))
            raise e


async def count_message_tokens(message_log):
    token_total = 0
    for m in message_log:
        token_total += math.floor((len(m['content'])-len(m['content'].replace(' ','').replace('\n','')))*3.5)+7

    return token_total


# Use openAI ChatGPT 3.5 Turbo chat completion end point
async def generate_chat_completion(message_log, model_name=C_MODELS[C_DEFAULT_MODEL_CODE]["model_name"], max_tokens=C_DEFAULT_COMPLETION_TOKENS, temperature=C_DEFAULT_TEMP, logit_bias=None):
    assert isinstance(message_log, list), "message log must be a list"
    assert len(message_log) > 0, "message log must not be empty"
    
    async def fcall():
        response = openai.chat.completions.create(
            model=model_name,
            messages=message_log,
            temperature=temperature,
            max_tokens=max_tokens,
            logit_bias=logit_bias or {}
        )
        return response.choices[0].message.content

    return await generic_retry_handler(fcall)


async def count_message_tokens_openai(message_log):
    async def fcall():
        response = await openai.ChatCompletion.acreate(
            model=C_MODELS[C_DEFAULT_MODEL_CODE]["model_name"],
            messages=message_log,
            temperature=0.0,
            max_tokens=1
        )
        return response["usage"]["prompt_tokens"]
    
    return await generic_retry_handler(fcall)



async def calculate_embeddings(content):

    async def fcall():
        result = openai.Embedding.create( input=content, model="text-embedding-ada-002")
        return result['data'][0]['embedding']
    
    return await generic_retry_handler(fcall)


def generate_image(description, quality="standard"):
    response = openai.images.generate(
        model="dall-e-3",
        prompt=description[:4000],
        size="1024x1024",
        quality=quality,
        n=1,
    )

    return response.data[0].url