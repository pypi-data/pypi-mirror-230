import json

from typing import Union
from abc import abstractmethod
from collections.abc import AsyncIterator, Iterator
from fastapi.responses import StreamingResponse


def transform_stream_data(content: Union[str, dict]) -> bytes:
    _data = (
        content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
    )
    return f"data: {_data}\n\n".encode("utf-8")


async def to_async_iterator(iterator):
    for i in iterator:
        yield i


class WrapStreamResponse:
    # todo

    def __init__(self, iterator) -> None:
        self.iterator = iterator

    def to_stream_response(self) -> StreamingResponse:
        for i in self.iterator:
            yield i
            return StreamingResponse(
                content=i,
                media_type="text/event-stream; charset=utf-8",
                headers={"Transfer-Encoding": "chunked"},
            )
