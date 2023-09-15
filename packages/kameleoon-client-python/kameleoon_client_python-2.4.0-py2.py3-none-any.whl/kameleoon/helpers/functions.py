"""Helper functions"""
import hashlib
import json
import math
import sys
from http.cookies import SimpleCookie
from secrets import token_urlsafe
from typing import Dict, Any, Optional, Union

from kameleoon.defaults import (
    KAMELEOON_COOKIE_VALUE_LENGTH,
    KAMELEOON_VISITOR_CODE_LENGTH,
    KAMELEOON_COOKIE_NAME,
    KAMELEOON_KEY_JS_COOKIE,
)
from kameleoon.exceptions import VisitorCodeNotValid


def obtain_hash_double(
    visitor_code: str, respool_times=None, container_id: str = ""
) -> float:
    """Calculate the hash value for a given visitor_code"""
    return _obtain_hash_double(visitor_code, respool_times, container_id)


def obtain_hash_double_rule(
    visitor_code: str, container_id: int, respool_time: Optional[int] = None
) -> float:
    """Calculate the hash value for feature flag v2 for a given visitor_code"""
    return _obtain_hash_double(
        visitor_code=visitor_code,
        container_id=container_id,
        suffix=str(respool_time) if respool_time else "",
    )


def _obtain_hash_double(
    visitor_code: str,
    respool_times=None,
    container_id: Union[str, int] = "",
    suffix: str = "",
) -> float:
    if respool_times is None:
        respool_times = {}
    identifier = visitor_code
    identifier += str(container_id)
    identifier += suffix
    if respool_times:
        identifier += "".join([str(v) for k, v in sorted(respool_times.items())])
    return int(hashlib.sha256(identifier.encode("UTF-8")).hexdigest(), 16) / math.pow(
        2, 256
    )


def load_params_from_json(json_path) -> Dict[Any, Any]:
    """Load json for a file"""
    with open(json_path, encoding="utf-8") as file:
        return json.load(file)


def get_size(obj) -> float:
    """Get size of memory used by given obj"""
    return sum([sys.getsizeof(v) + sys.getsizeof(k) for k, v in obj.items()])


def check_visitor_code(default_visitor_code: str) -> str:
    """
    default_visitor_code validation
    :param default_visitor_code:
    :type default_visitor_code: str
    :return: default_visitor_code
    """
    if len(default_visitor_code) > KAMELEOON_VISITOR_CODE_LENGTH:
        raise VisitorCodeNotValid("is longer than 255 chars")
    if default_visitor_code == "":
        raise VisitorCodeNotValid("empty visitor code")
    return default_visitor_code


def read_kameleoon_cookie_value(
    cookies: Union[str, Dict[str, str]], default_visitor_code: Union[str, None]
) -> str:
    """
    Reading kameleoon cookie value from cookies.
    :param default_visitor_code:
    :type default_visitor_code: str
    :param cookies: str ot dict
    :return: str or None
    """
    cookie: Any = SimpleCookie()
    cookie.load(cookies)
    kameleoon_cookie = cookie.get(KAMELEOON_COOKIE_NAME)
    if kameleoon_cookie:
        kameleoon_cookie_value = kameleoon_cookie.value
        if kameleoon_cookie_value.startswith(KAMELEOON_KEY_JS_COOKIE):
            kameleoon_cookie_value = kameleoon_cookie_value[
                len(KAMELEOON_KEY_JS_COOKIE) :
            ]
        return kameleoon_cookie_value
    if default_visitor_code or default_visitor_code == "":
        return check_visitor_code(default_visitor_code)
    return token_urlsafe(KAMELEOON_COOKIE_VALUE_LENGTH)
