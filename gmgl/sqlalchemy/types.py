# GMG Copyright 2022 - Alexandre Díaz
import sqlalchemy.types as types
from sqlalchemy.ext.mutable import MutableDict
from gmgl.utils import bin2b64, b642bin


class JSONEncoded(types.TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage::
        JSONEncoded(255)
    """

    impl = types.String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value if value is None else json.dumps(value)

    def process_result_value(self, value, dialect):
        return value if value is None else json.loads(value)


JSONEncodedMutable = MutableDict.as_mutable(JSONEncoded)


class BinaryBase64Encoded(types.TypeDecorator):
    """Represents an text as a base64-enconded string

    Usage::
        Base64Encoded()
    """

    impl = types.Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return bin2b64(value)

    def process_result_value(self, value, dialect):
        return b642bin(value)
