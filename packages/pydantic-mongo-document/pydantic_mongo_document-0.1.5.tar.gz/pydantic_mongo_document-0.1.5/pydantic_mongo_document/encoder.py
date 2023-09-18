import json
from enum import Enum
from typing import Any

import bson
from pydantic import BaseModel, SecretStr


class JsonEncoder(json.JSONEncoder):
    def encode(self, o: Any, reveal_secrets: bool = False) -> Any:
        if isinstance(o, Enum):
            return o.value

        if isinstance(o, BaseModel):
            return o.model_dump_json()

        if isinstance(o, bson.ObjectId):
            return str(o)

        if isinstance(o, (set, list, tuple)):
            return [self.encode(item) for item in o]

        if isinstance(o, dict):
            return self.encode_dict(o, reveal_secrets=reveal_secrets)

        if isinstance(o, SecretStr) and reveal_secrets:
            return o.get_secret_value()

        if isinstance(o, SecretStr):
            return str(o)

        if isinstance(o, (int, float, str, bool)):
            return o

        if o is None:
            return None

        return super().encode(o)

    def encode_dict(self, obj: dict[str, Any], reveal_secrets: bool = False) -> dict[str, Any]:
        """Encodes all values in dict."""

        encoded = {}
        for key, value in obj.items():
            if isinstance(value, dict):
                encoded[key] = self.encode_dict(value, reveal_secrets=reveal_secrets)
            else:
                encoded[key] = self.encode(value, reveal_secrets=reveal_secrets)

        return encoded
