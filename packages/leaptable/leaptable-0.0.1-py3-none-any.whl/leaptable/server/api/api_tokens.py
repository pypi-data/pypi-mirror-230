from fastapi import APIRouter, Depends, HTTPException, status

from leaptable.server.lib.api_key import generate_api_key
from leaptable.server.lib.auth.prisma import JWTBearer, decodeJWT
from leaptable.server.lib.db_models.api_key import ApiKey
from leaptable.server.lib.prisma import prisma

router = APIRouter()


@router.post(
    "/api_key", name="Create API token", description="Create a new API token"
)
async def create_api_key(body: ApiKey, token=Depends(JWTBearer())):
    """Create api token endpoint"""
    decoded = decodeJWT(token)
    token = generate_api_key()

    try:
        agent = prisma.apitoken.create(
            {
                "description": body.description,
                "token": token,
                "userId": decoded["userId"],
            },
            include={"user": True},
        )

        return {"success": True, "data": agent}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e,
        )


@router.get("/api-tokens", name="List API tokens", description="List all API tokens")
async def read_api_keys(token=Depends(JWTBearer())):
    """List api tokens endpoint"""
    decoded = decodeJWT(token)
    api_keys = prisma.apitoken.find_many(
        where={"userId": decoded["userId"]}, include={"user": True}
    )

    if api_keys:
        return {"success": True, "data": api_keys}

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="No agents found",
    )


@router.get(
    "/api-tokens/{tokenId}",
    name="Get API token",
    description="Get a specific API token",
)
async def read_api_key(tokenId: str, token=Depends(JWTBearer())):
    """Get an api token endpoint"""
    api_key = prisma.apitoken.find_unique(
        where={"id": tokenId}, include={"user": True}
    )

    if api_key:
        return {"success": True, "data": api_key}

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"API token with id: {tokenId} not found",
    )


@router.delete(
    "/api-tokens/{tokenId}",
    name="Delete API token",
    description="Delete a specific API token",
)
async def delete_api_key(tokenId: str, token=Depends(JWTBearer())):
    """Delete api token endpoint"""
    try:
        prisma.apitoken.delete(where={"id": tokenId})

        return {"success": True, "data": None}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e,
        )
