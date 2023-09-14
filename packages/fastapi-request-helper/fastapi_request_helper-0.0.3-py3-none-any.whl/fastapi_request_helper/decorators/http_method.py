from typing import Any, Optional, Type, TypeVar

from fastapi import Depends
from fastapi import status as status_code
from fastapi.types import IncEx

from ..constants.http_method import DELETE, GET, PATCH, POST, PUT
from ..dependencies.guard import create_guard
from ..helpers.router_decorator import add_element_to_api_detail, set_api_detail

T = TypeVar('T')


def single_key_decorator(key, value: Any):
    def decorator(cls: Type[T]):
        set_api_detail(cls, key, value)
        return cls

    return decorator


def http_method(method: str, path: Optional[str] = None):
    if path is None:
        path = ''
    else:
        path = '/' + path

    def decorator(cls: Type[T]):
        set_api_detail(cls, 'methods', [method])
        set_api_detail(cls, 'path', path)
        return cls

    return decorator


def get(path: Optional[str] = None):
    return http_method(GET, path)


def post(path: Optional[str] = None):
    return http_method(POST, path)


def put(path: Optional[str] = None):
    return http_method(PUT, path)


def delete(path: Optional[str] = None):
    return http_method(DELETE, path)


def patch(path: Optional[str] = None):
    return http_method(PATCH, path)


def response(
    model: Any = None,
    response_description: str = 'Successful Response',
    model_include: Optional[IncEx] = None,
    model_exclude: Optional[IncEx] = None,
    model_by_alias: bool = True,
    model_exclude_unset: bool = False,
    model_exclude_defaults: bool = False,
    model_exclude_none: bool = False,
):
    def decorator(cls: Type[T]):
        set_api_detail(cls, 'response_model', model)
        set_api_detail(cls, 'response_description', response_description)
        set_api_detail(cls, 'response_model_include', model_include)
        set_api_detail(cls, 'response_model_exclude', model_exclude)
        set_api_detail(cls, 'response_model_by_alias', model_by_alias)
        set_api_detail(cls, 'response_model_exclude_unset', model_exclude_unset)
        set_api_detail(cls, 'response_model_exclude_defaults', model_exclude_defaults)
        set_api_detail(cls, 'response_model_exclude_none', model_exclude_none)
        return cls

    return decorator


def guard(guard_dependency):
    def decorator(cls: Type[T]):
        add_element_to_api_detail(cls, 'dependencies', Depends(create_guard(guard_dependency)))
        return cls

    return decorator


def guards(*guard_dependencies):
    def decorator(cls: Type[T]):
        for guard in guard_dependencies:
            add_element_to_api_detail(cls, 'dependencies', Depends(create_guard(guard)))
        return cls

    return decorator


def rate_limit(times: int, ttl: float = 1, status: int = None):
    def decorator(cls: Type[T]):
        # TODO: add rate_limit to swagger extension
        return cls

    return decorator


def status(value: int):
    return single_key_decorator('status_code', value)


def description(value: str):
    return single_key_decorator('description', value)


def summary(value: str):
    return single_key_decorator('summary', value)


def name(value: str):
    return single_key_decorator('name', value)


def tag(value: str):
    return single_key_decorator('tags', [value])


def status_no_content():
    return single_key_decorator('status_code', status_code.HTTP_204_NO_CONTENT)


def read_only():
    def decorator(cls: Type[T]):
        setattr(cls, 'read_only', True)
        return cls

    return decorator


def status_ok():
    return single_key_decorator('status_code', status_code.HTTP_200_OK)


def status_created():
    return single_key_decorator('status_code', status_code.HTTP_201_CREATED)


def hidden_when(is_hidden: bool):
    is_showed_in_doc = False if is_hidden else True
    return single_key_decorator('include_in_schema', is_showed_in_doc)
