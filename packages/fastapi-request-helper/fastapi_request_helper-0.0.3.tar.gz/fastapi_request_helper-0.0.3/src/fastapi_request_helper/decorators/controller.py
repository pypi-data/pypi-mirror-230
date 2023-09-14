import inspect
from typing import Any, Callable, Optional, Type, TypeVar

from fastapi_global_variable import GlobalVariable
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

T = TypeVar('T')


def controller(prefix: Optional[str] = None) -> Callable[[Type[T]], Type[T]]:
    def decorator(cls: Type[T]) -> Type[T]:
        router = InferringRouter()
        add_function_routers(prefix, cls, router)
        cbv(router)(cls)
        GlobalVariable.get_or_fail('app').include_router(router)

        return cls

    return decorator


def add_function_routers(prefix: str, cls: Type[T], router: InferringRouter):
    function_members = inspect.getmembers(cls, inspect.isfunction)
    parent_detail = {}
    if hasattr(cls, 'api_detail'):
        parent_detail = getattr(cls, 'api_detail')

    for function_member in function_members:
        add_function_router(prefix, function_member, router, parent_detail)


def add_function_router(
    prefix: str,
    function_member: tuple[str, Any],
    router: InferringRouter,
    parent_detail: dict,
):
    function_body = function_member[1]

    if hasattr(function_body, 'api_detail'):
        api_detail = getattr(function_body, 'api_detail')
        api_detail = combine_api_detail(parent_detail, api_detail)
        if api_detail['path'] is not None:
            api_detail['path'] = '/' + prefix + api_detail['path']
            router.api_route(**api_detail)(function_body)


def combine_api_detail(parent_detail: dict, api_detail: dict):
    if parent_detail:
        for key in parent_detail.keys():
            if key not in api_detail:
                api_detail[key] = parent_detail[key]
            else:
                if isinstance(api_detail[key], list):
                    for item in parent_detail[key]:
                        api_detail[key].append(item)
    return api_detail
