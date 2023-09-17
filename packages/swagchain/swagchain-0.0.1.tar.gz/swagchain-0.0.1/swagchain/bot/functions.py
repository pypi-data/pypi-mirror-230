import json
from abc import ABC, abstractmethod
from typing import Any, List, Type, TypeVar

import openai
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

F = TypeVar("F", bound="OpenAIFunction")


class FunctionCall(BaseModel):
    name: str
    data: Any


class OpenAIFunction(BaseModel, ABC):
    class Metadata:
        subclasses: List[Type[F]] = []

    @classmethod
    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        _schema = cls.schema()
        if cls.__doc__ is None:
            raise ValueError(
                f"OpenAIFunction subclass {cls.__name__} must have a docstring"
            )
        cls.openaischema = {
            "name": cls.__name__,
            "description": cls.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    k: v for k, v in _schema["properties"].items() if k != "self"
                },
                "required": list(_schema["required"]),
            },
        }
        cls.Metadata.subclasses.append(cls)

    async def __call__(self, **kwargs: Any) -> FunctionCall:
        response = await self.run(**kwargs)
        return FunctionCall(name=self.__class__.__name__, data=response)

    @abstractmethod
    async def run(self, **kwargs: Any) -> Any:
        ...


async def parse_openai_function(
    response: dict,
    functions: List[Type[F]] = OpenAIFunction.Metadata.subclasses,
    **kwargs: Any,
) -> FunctionCall:
    choice = response["choices"][0]["message"]
    if "function_call" in choice:
        function_call_ = choice["function_call"]
        name = function_call_["name"]
        arguments = function_call_["arguments"]
        for i in functions:
            if i.__name__ == name:
                result = await i(**json.loads(arguments))(**kwargs)
                break
        else:
            raise ValueError(f"Function {name} not found")
        return result
    return FunctionCall(name="chat", data=choice["content"])


async def function_call(
    text: str,
    model: str = "gpt-3.5-turbo-16k-0613",
    functions: List[Type[F]] = OpenAIFunction.Metadata.subclasses,
    **kwargs,
) -> FunctionCall:
    messages = [
        {"role": "user", "content": text},
        {"role": "system", "content": "You are a function Orchestrator"},
    ]
    response = await openai.ChatCompletion.acreate(
        model=model,
        messages=messages,
        functions=[i.openaischema for i in functions],
    )
    return await parse_openai_function(response, functions=functions, **kwargs)


async def chat_completion(text: str, context: Optional[str] = None):
    if context is not None:
        messages = [
            {"role": "user", "content": text},
            {"role": "system", "content": context},
        ]
    else:
        messages = [{"role": "user", "content": text}]
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo-16k-0613", messages=messages
    )
    return response["choices"][0]["message"]["content"]
