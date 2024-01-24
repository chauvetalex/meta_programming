import re
import requests
import pathlib
import logging
import json
from functools import wraps
import time
from typing import Optional
import logging
from configparser import ConfigParser, NoSectionError, NoOptionError

'wizardcoder:7b-python'
'wizardcoder:13b-python'
'codellama:7b-python'
'codellama:13b-python'
'codellama:13b-instruct'

google_template =     """[Description]]:

    Args:
        param1 (type): The first parameter description.
        param2 (type): The second parameter description.

    Returns:
        type: The return value description."""

local_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Read config file and set parameters.
config = ConfigParser()
config.read('config.ini')
LLM_BASE_URL = config.get('ollama', 'url') + '/'
model = config.get('ollama', 'model')

system_prompt = "You are a coding assistant. You help coders documenting their code, by providing detailed docstrings and comments. You use type annotations and google style docstrings."


def _get_prompts_from_config(key):
    try:
        specific_val = config.get(model, key)
        if specific_val:
            return config.get(model, key)
    except (NoSectionError, NoOptionError) as err:
        logging.debug(err)
        return config.get('default_prompts', key)


# Define a timer decorator for testing purposes.
def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper


def generate_comments(undoc_code:str, inline:bool=False) -> str:

    inline_comments = "Add inline comments to the method body where it makes sense." if inline else ""
    main_prompt = \
    f"""Add detailed docstrings and comments to the following python methods:\n{undoc_code}\n.
    The docstrings should describe what the methods do. {inline_comments}
    Use type annotations.
    Use google style docstrings with is {google_template}
    Apart from types annotations, comments and docstrings, do not alter code.
    Do not include any explanations in your response.
    """

    url = LLM_BASE_URL + 'generate'
    data = {
        'model':model,
        'system_prompt':system_prompt,
        'prompt': main_prompt,
        "stream": False,
        'options':{'temperature':0}
    }
    response = requests.post(
        url,
        json=data
    )
    translation = json.loads(response.text)['response']

    return translation



if __name__ == '__main__':
    app = 'data/app_2.py'
    with open(app, 'r') as f:
        undoc_code = f.read()
    doc_code = generate_comments(undoc_code, inline=True)
    with open(f'data/doc_{app}', 'w') as f:
        f.write(doc_code)
