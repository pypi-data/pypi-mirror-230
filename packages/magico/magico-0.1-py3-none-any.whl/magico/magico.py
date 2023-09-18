from .dotted_dict import *
from abc import ABC
from typing import Any, Union, Callable
from copy import deepcopy
import json
import re
import functools

# import logging
# logging.basicConfig()
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)


class MagicO(ABC):
    def __init__(self, data: Union[dict, list]) -> None:
        # Use only __dict__ to avoid triggering magic functions
        # self._data = data
        # self._type_method_list = []
        self.__dict__["_data"] = data
        self.__dict__["_type_method_list"] = []
        data_type = type(data)
        if data_type == dict:
            self.__dict__["_type_method_list"] = [
                "clear",
                "copy",
                "fromkeys",
                "get",
                "items",
                "keys",
                "pop",
                "popitem",
                "setdefault",
                "update",
                "values",
            ]
        elif data_type == list:
            self.__dict__["_type_method_list"] = [
                "append",
                "clear",
                "copy",
                "count",
                "extend",
                "index",
                "insert",
                "pop",
                "remove",
                "reverse",
                "sort",
            ]

        for type_method in self.__dict__["_type_method_list"]:
            self.__dict__[type_method] = self._type_method(data_type, type_method)


    def _type_method(self, type: type, method_name: str) -> Callable:
        type_method = getattr(type, method_name)
        # logger.debug(f"_type_method: {type_method}")
        @functools.wraps(type_method)
        def method_wrapper(*args, **kwargs):
            return type_method(self.__dict__["_data"], *args, **kwargs)
        return method_wrapper


    def __len__(self) -> int:
        return len(self._data)


    def __str__(self) -> str:
        if type(self._data) == dict:
            return json.dumps(self._data)
        else:
            return str(self._data)


    def __repr__(self) -> str:
        return str(self._data)


    def __bool__(self) -> bool:
        return self._data != {} and self._data != []


    def __contains__(self, other) -> bool:
        return self.__getitem__(other) != None


    def __iter__(self) -> list:
        return self._data.__iter__()


    def __getattr__(self, attr) -> Any:
        # logger.debug(f"__getattr__: {type(attr)} {attr}")
        if attr in self.__dict__["_type_method_list"]:
            return self.__dict__["_type_method_list"][attr]
        elif attr in self._data:
            if type(self._data[attr]) in (dict, list):
                return MagicO(self._data[attr])
            else:
                return self._data[attr]
        else:
            raise Exception(f"{type(self).__name__} object has no attribute '{attr}'")


    def __setattr__(self, attr, value: Any) -> None:
        # logger.debug(f"__setattr__:  {type(attr)} {attr} <- {value}")
        # Use self.__dict__ to avoid recursion
        if "_data" not in self.__dict__:
            # Set the first _data attribute
            self._data = {attr: value}
        else:
            # self._data exists
            self._data[attr] = value


    def __delattr__(self, attr: str) -> None:
        # logger.debug(f"__getattr__: {type(attr)} {attr}")
        if "_data" in self.__dict__ and attr in self._data:
            del self._data[attr]


    def __getitem__(self, path) -> Any:
        # logger.debug(f"__getitem__: {type(path)} {path}")
        if type(path) == str:
            return dotted_dict(self._data, path_str(path))
        else:
            item = dotted_dict(self._data, path_str(path))
            if type(item) in (dict, list):
                item = MagicO(item)
            return item


    def __setitem__(self, path, value) -> None:
        # logger.debug(f"__setitem__: {type(path)} {path} <- {value}")
        dotted_dict(self._data, path_str(path), value=value)


    def __delitem__(self, path) -> None:
        # logger.debug(f"__delitem__: {type(path)} {path}")
        dotted_dict(self._data, path_str(path), delete=True)


    def to_data(self) -> Union[dict, list]:
        # logger.debug(f"to_data: {type(self._data)} {self._data}")
        return self._data


    def to_dict(self) -> Union[dict, list]:
        # logger.debug(f"to_dict: {type(self._data)} {self._data}")
        return self._data


    def to_list(self) -> Union[dict, list]:
        # logger.debug(f"to_list: {type(self._data)} {self._data}")
        return self._data
