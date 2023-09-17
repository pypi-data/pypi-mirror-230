import functools
from dataclasses import dataclass, field
from typing import (
    AsyncGenerator,
    Callable,
    Dict,
    List,
    Literal,
    TypeAlias,
    TypeVar,
    Union,
)

import openai  # pylint-disable=E0401
from aiofauna import Document, Field  # type: ignore
from jinja2 import Template
from typing_extensions import ParamSpec

T = TypeVar("T")
P = ParamSpec("P")

Role: TypeAlias = Literal["assistant", "user", "system", "function"]
Model: TypeAlias = Literal["gpt-4-0613", "gpt-3.5-turbo-16k-0613"]
Size: TypeAlias = Literal["256x256", "512x512", "1024x1024"]
Format: TypeAlias = Literal["url", "base64"]


class Message(Document):
    role: Role = Field(..., description="The role of the message")
    content: str = Field(..., description="The content of the message")


class ChatCompletionRequest(Document):
    model: Model = Field(..., description="The model to use for the completion")
    messages: List[Message] = Field(
        ..., description="The messages to use for the completion"
    )
    temperature: float = Field(
        default=0.5, description="The temperature of the completion"
    )
    max_tokens: int = Field(
        1024, description="The maximum number of tokens to generate"
    )
    stream: bool = Field(False, description="Whether to stream the completion or not")


class ChatCompletionUssage(Document):
    prompt_tokens: int = Field(..., description="The number of tokens in the prompt")
    completion_tokens: int = Field(
        ..., description="The number of tokens in the completion"
    )
    total_tokens: int = Field(..., description="The total number of tokens")


class ChatCompletionChoice(Document):
    index: int = Field(..., description="The index of the choice")
    message: Message = Field(..., description="The message of the choice")
    finish_reason: str = Field(..., description="The reason the choice was finished")


class ChatCompletionResponse(Document):
    id: str = Field(..., description="The id of the completion")
    object: str = Field(..., description="The object of the completion")
    created: int = Field(..., description="The creation time of the completion")
    model: Model = Field(..., description="The model used for the completion")
    choices: List[ChatCompletionChoice] = Field(
        ..., description="The choices of the completion"
    )
    usage: ChatCompletionUssage = Field(..., description="The usage of the completion")
    stream: bool = Field(..., description="Whether the completion was streamed or not")


class VectorResponse(Document):
    text: str = Field(..., description="The text of the completion")
    score: float = Field(..., description="The score of the completion")


class CreateImageResponse(Document):
    created: float = Field(...)
    data: List[Dict[Format, str]] = Field(...)


class CreateImageRequest(Document):
    prompt: str = Field(...)
    n: int = Field(default=1)
    size: Size = Field(default="1024x1024")
    response_format: Format = Field(default="url")


@dataclass(init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)
class ChatGPT:
    model: Model = field(default="gpt-4-0613")
    temperature: float = field(default=0.2)
    max_tokens: int = field(default=1024)
    stream: bool = field(default=False)

    async def chat(
        self, messages: List[Message]
    ) -> Union[AsyncGenerator[str, None], str]:
        response = openai.ChatCompletion.acreate(  # type: ignore
            model=self.model,
            messages=[message.dict() for message in messages],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=self.stream,
        )
        if self.stream:
            async for completion in response:  # type: ignore
                chunk: str = completion.choices[0].delta.get("content")  # type: ignore
                if chunk is not None:
                    yield chunk
                else:
                    break
        else:
            return response.choices[0].message.content  # type: ignore

    def __call__(self, func: Callable[P, Union[AsyncGenerator[str, None], str]]):
        @functools.wraps(func)
        async def wrapper(
            text: str, *args: P.args, **kwargs: P.kwargs
        ) -> Union[str, AsyncGenerator[str, None]]:
            if func.__doc__ is None:
                raise ValueError("The function must have a docstring")
            template = Template(func.__doc__)
            sys_message = Message(role="system", content=template.render(**kwargs))
            messages = [sys_message, Message(role="user", content=text)]
            return await self.chat(messages)

        return wrapper
