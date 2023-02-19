import json
from typing import Any

from .abc import Serializer


class JsonSerializer(Serializer):
    def dumps(self, payload: Any) -> bytes:
        return json.dumps(payload).encode()

    def loads(self, data: bytes) -> Any:
        return json.loads(data)
