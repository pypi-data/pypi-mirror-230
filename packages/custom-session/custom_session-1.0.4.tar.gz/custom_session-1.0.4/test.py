import os
import openai
from dataclasses import dataclass, field
from dotenv import dotenv_values
from typing import *


@dataclass
class SystemSettings:
    bot_token: str
    main_server_id: int
    owner_id: int
    mass_domains: List[str] = field(default_factory=list, init=False)
    embed_color: int | str
    logo: str

    def __post_init__(self):
        self.bot_token = str(self.bot_token)
        self.main_server_id = int(self.main_server_id)
        self.owner_id = int(self.owner_id)
        self.mass_domains = [".com", ".co.uk", ".com.au"]
        self.embed_color = int(self.embed_color, 0)
        self.logo = str(self.logo)

def load_env_vars() -> SystemSettings:
  env_vars = dict(dotenv_values())
  new = {}
  for index, (key, value) in enumerate(env_vars.items()):
    new[key.lower()] = value
  lower_case_settings = dict(map(lambda x: (x[0].lower(), x[1]), env_vars.items()))
  return SystemSettings(**lower_case_settings)
  # SystemSettings(**map(dict(env_vars)))

openai.api_key = "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"

with open("CustomSession/models.py", "r") as f:
  content = f.read()

print(repr(content))
response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {
      "role": "system",
      "content": "You are a program that writes docstrings for Python classes and functions. Follow the rules outlined below. Follow the output format outlined below. Follow the docstring format outlined below.\n\nRules:\n- Format your response to be the same as the given output format detailed below\n- Format docstrings based on the given example docstring format\n- Provide usage examples only when writing a docsting for a class\n- If you are provided with a class and it has functions, write docstrings for both the class and each function\n\nClass Docstring Example Format:\n\"\"\"\n    An asynchronous HTTP client inherited from httpx.AsyncClient that maintains unique a user-agent, metadata, and proxy.\n\n    Usage:\n\n    ```\n    async with AsyncSession() as client:\n        response = await client.get('https://example.org')\n    ```\n\n    **Parameters:**\n    * **proxy** - *(optional)* HTTP/s proxy to use when sending\n    requests.\n    * **ignore_exceptions** - *(optional)* Tuple of Exceptions to be ignored when sending requests\n    * **auth** - *(optional)* An authentication class to use when sending\n    requests.\n    * **meta_data** - *(optional)* A dict to use when persistent miscellaneous session data is required\n\"\"\"\n\nFunction Docstring Example Format:\n\"\"\"\n        Send an HTTP GET request with optional retries.\n\n        :param url: The URL to send the GET request to.\n        :param retries: The number of times to retry the request in case of exceptions.\n        :param params: (optional) Query parameters to include in the request.\n        :param headers: (optional) Headers to include in the request.\n        :param cookies: (optional) Cookies to include in the request.\n        :param follow_redirects: (optional) Whether to follow redirects or use the client's default behavior.\n        :param timeout: (optional) The request timeout or use the client's default timeout.\n        :param extensions: (optional) Extensions to include in the request.\n\n        :return: The HTTP response object.\n\n        :raises RetriesExceeded: If the maximum number of retries is exceeded.\n\"\"\"\n\nOutput Format:\n\n## {function/class name}\n\n{docstring}"
    },
    {
      "role": "user",
      "content": content
    }
  ],
  temperature=1,
  max_tokens=256,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)
print(response)