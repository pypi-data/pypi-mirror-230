import pandas as pd
from cognite.client import CogniteClient

is_patched = False
async def patch_cognite():
    # TODO: This is a series of hacks to make pandasai work in JupyterLite
    # Multiple of these hacks are workarounds for aiohttp 3.6.2 does not work
    # with Python 3.11, and later packages don't exist as pure python wheels.
    # However, we are not using them, this is only happening because openai is not
    # an optional package, and we are providing our own LLM into this mix.
    # In addition, we are using a wip duckdb implementation which can be fully
    # mocked as long as we don't use caching.

    global is_patched
    if is_patched:
        return
    
    import micropip

    await micropip.install("pandasai==1.2.2", deps=False)
    await micropip.install("pydantic==1.10.7")
    await micropip.install("distutils=1.0.0")
    await micropip.install("openai==0.28.0", deps=False)
    await micropip.install("aiohttp==3.6.2", deps=False)
    await micropip.install("attrs==22.2.0")
    await micropip.install("yarl==1.8.2")
    await micropip.install("async_timeout==4.3.0")
    await micropip.install("chardet==5.2.0")
    await micropip.install("astor==0.8.1")
    await micropip.install("sqlalchemy==2.0.7")
    await micropip.install("beautifulsoup4==4.12.0")
    await micropip.install('jupylite-duckdb==0.0.17')

    # This creates errors due to Python 3.11. This patch hides the problem.
    with open("/lib/python3.11/site-packages/aiohttp/helpers.py") as f:
        lines = f.readlines()
    with open("/lib/python3.11/site-packages/aiohttp/helpers.py", "w") as f:
        for i, line in enumerate(lines):
            if i < 605:
                f.write(line)
            elif i == 605:
                f.write("class CeilTimeout():\n    def __enter__(self) -> async_timeout.timeout:\n        pass")
            elif i < 618:
                continue
            else:
                f.write(line)

    # This creates errors due to dotenv not being available in Pyodide environments. Just mock the function.
    with open("/lib/python3.11/site-packages/pandasai/helpers/env.py") as f:
        lines = f.readlines()
    with open("/lib/python3.11/site-packages/pandasai/helpers/env.py", "w") as f:
            f.write("""
    def _load_dotenv(dotenv_path):
        pass

    """)
            for i in range(1,len(lines)):
                f.write(lines[i])
    
    # Patch duckdb, not in use if cache is disabled.
    with open("/lib/python3.11/site-packages/pandasai/helpers/cache.py") as f:
        lines = f.readlines()
    with open("/lib/python3.11/site-packages/pandasai/helpers/cache.py", "w") as f:
        for i, line in enumerate(lines):
            if i == 2:
                f.write("import jupylite_duckdb as duckdb\n")
            else:
                f.write(line)
    
    # Patch some missing features in asyncio.
    import asyncio
    asyncio.coroutines._DEBUG = False
    import asyncio

    def noop_decorator(func):
        return func

    # Assign the noop_decorator to asyncio.coroutine
    asyncio.coroutine = noop_decorator

patch_cognite()

from pandasai.ai import LLM
from pandasai import SmartDataframe as SDF

class CogniteLLM(LLM):
    api_token: str
    temperature = 0
    max_tokens = 1000
    frequency_penalty = 0
    presence_penalty = 0.6
    stop = None

    def __init__(self, cognite_client):
        LLM.__init__(self)
        self.cognite_client = cognite_client
    def _set_params(self, **kwargs):
        """
        Set Parameters
        Args:
            **kwargs: ["model", "engine", "deployment_id", "temperature","max_tokens",
            "top_p", "frequency_penalty", "presence_penalty", "stop", ]

        Returns:
            None.

        """

        valid_params = [
            "model",
            "engine",
            "deployment_id",
            "temperature",
            "maxTokens",
            "frequencyPenalty",
            "presencePenalty",
            "stop",
        ]
        for key, value in kwargs.items():
            if key in valid_params:
                setattr(self, key, value)

    @property
    def _default_params(self):
        """
        Get the default parameters for calling OpenAI API

        Returns
            Dict: A dict of OpenAi API parameters.

        """

        return {
            "temperature": self.temperature,
            "maxTokens": self.max_tokens,
            "frequencyPenalty": self.frequency_penalty,
            "presencePenalty": self.presence_penalty,
        }

    def chat_completion(self, value):
        body = {
                "messages": [
                    {
                        "role": "system",
                        "content": value,
                    }
                ],
                **self._default_params,
            }
        response = self.cognite_client.post(
            url=f"/api/v1/projects/{client.config.project}/gpt/chat/completions",
            json=body
        )
        return response.json()["choices"][0]["message"]["content"]
    
    def call(self, instruction, suffix = ""):
        self.last_prompt = instruction.to_string() + suffix
        
        response = self.chat_completion(self.last_prompt)
        return response

    @property
    def type(self) -> str:
        return "cognite"

        
class SmartDataframe(SDF):
    def __init__(self, df: pd.DataFrame, cognite_client: CogniteClient):
        self.llm = CogniteLLM(cognite_client=cognite_client)
        super().__init__(df, config={"llm": self.llm, "enable_cache": False})
