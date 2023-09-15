from collections import namedtuple

class DotWrapper:
    def __init__(self, obj, visited=None, max_depth=1000, depth=0):
        self.__dict__["_value"] = None  # Initialize _value directly in __dict__
        
        if visited is None:
            visited = set()

        if depth > max_depth:
            raise RecursionError("Maximum recursion depth exceeded")

        if id(obj) in visited:
            self._value = "Circular Reference Detected"
            return

        visited.add(id(obj))

        if isinstance(obj, (int, float, str, list, tuple)):
            self._value = obj
        elif isinstance(obj, dict):
            for key, value in obj.items():
                if not isinstance(key, str):
                    continue  # Skip non-string keys
                if isinstance(value, (int, float, str, list, tuple)):
                    setattr(self, key, value)
                else:
                    setattr(self, key, DotWrapper(value, visited, max_depth, depth + 1))
        elif hasattr(obj, "__dict__"):
            for key, value in obj.__dict__.items():
                if key.startswith("__") or key in ['__dict__', '__weakref__'] or not isinstance(key, str):
                    continue  # Skip special attributes and non-string keys
                if isinstance(value, (int, float, str, list, tuple)):
                    setattr(self, key, value)
                else:
                    setattr(self, key, DotWrapper(value, visited, max_depth, depth + 1))
        else:
            self._value = obj

    def __getattr__(self, attr):
        if attr == "_value":
            return self.__dict__.get("_value", None)
        return None

    def to_dict(self):
        if self._value is not None:
            return self._value
        else:
            result = {}
            for key, value in self.__dict__.items():
                if key == "_value":
                    continue
                if isinstance(value, DotWrapper):
                    result[key] = value.to_dict()
                else:
                    result[key] = value
            return result

    def __repr__(self):
        return repr(self.to_dict())
    

PostgresSettings = namedtuple('PostgresSettings', ['host', 'database', 'user', 'password', 'port'])
