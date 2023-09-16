from fastapi import APIRouter

from leaptable.server.api import (
    agents,
    namespace,
)

router = APIRouter()
api_prefix = "/api/v1"

router.include_router(agents.router, tags=["Agent"], prefix=api_prefix)
router.include_router(namespace.router, tags=["Namespace"], prefix=api_prefix)
