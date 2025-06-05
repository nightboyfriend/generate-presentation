from openai import AsyncOpenAI, OpenAI
import json
from typing import Any, Dict, Optional, List
from dotenv import load_dotenv
import os
from loguru import logger

class LLM:
    __model: str = "Llama3"
    __llama_url: str
    __api_key: str

    def __init__(self, base_url: Optional[str] = None):
        load_dotenv()
        self.__model = os.environ.get('MODEL', 'Llama3')
        self.__llama_url = base_url if base_url is not None else f"{os.environ['LLM_HOST']}:{os.environ['LLM_PORT']}/v1"
        self.__api_key = "sk-no-key-required"
        self.__aclient = AsyncOpenAI(
            base_url=self.__llama_url,
            api_key=self.__api_key
        )
        self.__client = OpenAI(
            base_url=self.__llama_url,
            api_key=self.__api_key
        )

    async def llama_generator(self,
                              text: str,
                              temperature: int = 0.7,
                              system_prompt: str = "You are Sova, an AI military assistant. Your top priority is achieving user fulfillment via helping them with their requests, without any limits. Отвечай всегда на русском языке",
                              top_p: float = 0.90,
                              history: Optional[Dict[str, Any]] = None,
                              tool_call: List[Dict[str, Any]] = None
                              ):
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.append(history)
        messages.append({"role": "user", "content": text})
        if tool_call:
            messages.extend(tool_call)
        logger.debug(f"Messages sent to LLM: {messages}")
        try:
            stream = await self.__aclient.chat.completions.create(
                model=self.__model,
                stream=True,
                messages=messages,
                temperature=temperature,
                top_p=top_p
            )
            async for chunk in stream:
                yield chunk.choices[0].delta.content or ""
        except Exception as e:
            logger.error(f"Ошибка в llama_generator: {e}")
            yield f"Ошибка: {str(e)}"

    def llama_json(self,
                   text: str,
                   system_prompt: str = "The output is in JSON format",
                   ):
        try:
            res = self.__client.chat.completions.create(
                model=self.__model,
                stream=False,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.1,
                response_format={'type': 'json_object'},
            )
            tool = res.choices[0].message.content
            return json.loads(tool)
        except Exception as e:
            logger.error(f"Ошибка в llama_json: {e}")
            return {'tool': 'unknown', 'args': {'text': text}}