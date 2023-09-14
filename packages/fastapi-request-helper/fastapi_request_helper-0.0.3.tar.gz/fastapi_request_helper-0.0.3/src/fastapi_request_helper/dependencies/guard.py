import asyncio

from fastapi import Depends


def create_guard(class_guard):
    async def guard(depend: class_guard = Depends(class_guard)):
        if asyncio.iscoroutinefunction(depend.validator):
            return await depend.validator()
        return depend.validator()

    return guard
