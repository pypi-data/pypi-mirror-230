#!/usr/bin/env python

__authors__ = ["Peter W. Njenga"]
__copyright__ = "Copyright © 2023 Leaptable, Inc."

# Standard Libraries
import json
from os import environ as os_env

# External Libraries
from fastapi import APIRouter, Request, Depends, HTTPException, status
from loguru import logger
from pprint import pformat, pprint
from psycopg import sql
from fastapi.encoders import jsonable_encoder

# Internal Libraries
from slugify import slugify
from uuid6 import uuid7

from leaptable.server.lib import sql_text
from leaptable.server.lib.api_key import generate_api_key
from leaptable.server.lib.db_connection import Database
from leaptable.server.lib.db_models.namespace import Namespace

# Global Variables
router = APIRouter()

class Serial(dict):
    def __getitem__(self, key):
        return f"${list(self.keys()).index(key) + 1}"

@router.post("/namespace/", name="Create Namespace", description="Create Workspace or Namespace")
async def create_namespace(request: Request, namespace: Namespace):
    """Agents endpoint"""
    try:
        # Check that the slug is valid. It should be in snake case, alphanumeric, and lowercase.
        if slugify(namespace.slug, separator='_') != namespace.slug:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid slug '{namespace.slug}'. Must be lowercase, alphanumeric, and snake case"
            )

        pprint(namespace.dict())

        try:
            namespace.data_db = Database(**namespace.data_db_params)
            await namespace.data_db.connect()
            request.app.state.data_db[str(namespace.id_)] = namespace.data_db

            namespace.trace_db = Database(**namespace.trace_db_params)
            await namespace.trace_db.connect()
            request.app.state.trace_db[str(namespace.id_)] = namespace.trace_db
        except Exception as e:
            logger.error(f"Error connecting to data database: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error connecting to data database: {e}"
            )  from None

        await request.app.state.meta_db.execute(
            """ 
            INSERT INTO namespace (_id, slug, name, data_db_params, trace_db_params)
            VALUES (%(id_)s, %(slug)s, %(name)s, %(data_db_params)s, %(trace_db_params)s)
            RETURNING _id, slug, name
            """, namespace.dict())

        logger.info(f"Created new namespace: {pformat(namespace.dict(include=['id_', 'name', 'slug']))}")

        api_key = generate_api_key()
        namespace.api_key = api_key
        await request.app.state.meta_db.execute(
            """
            INSERT INTO api_key (_id, key, namespace_id, name)
            VALUES (%(_id)s, %(key)s, %(namespace_id)s, %(name)s)
            RETURNING _id
            """, {
                "_id": uuid7(),
                "key": api_key,
                "namespace_id": namespace.id_,
                'name': f"Default API Key for {namespace.name}"
            })

        logger.info("Created new API Key")

        # Connect to the new database and create the trace schema
        await namespace.trace_db.execute("CREATE SCHEMA IF NOT EXISTS trace")


        await namespace.trace_db.execute("CREATE EXTENSION IF NOT EXISTS moddatetime;")


        # Create the trace tables
        tables = {
            'trace': sql_text.CREATE_TABLE_TRACE,
            'job': sql_text.CREATE_TABLE_JOB,
            'thread': sql_text.CREATE_TABLE_THREAD,
            'agent': sql_text.CREATE_TABLE_AGENT,
            'tool': sql_text.CREATE_TABLE_TOOL,
        }

        for table_name, table_sql in tables.items():
            await namespace.trace_db.execute(table_sql.format(table_name=table_name))
            logger.info(f"Created new table: {table_name}")

        logger.info(f"Done initializing namespace: {pformat({k : namespace.dict()[k] for k in ['id_', 'name', 'slug']})}")


        return {"success": True, "data": {k : namespace.dict()[k] for k in ['id_', 'name', 'slug', 'api_key']}}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )




@router.get("/namespace/", name="List all namespaces", description="List all namespaces")
async def list_agents():
    """Agents endpoint"""
    decoded = decodeJWT(token)
    agents = prisma.agent.find_many(
        where={"userId": decoded["userId"]},
        include={
            "user": True,
        },
        order={"createdAt": "desc"},
    )

    if agents:
        return {"success": True, "data": agents}

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="No agents found",
    )


@router.get("/namespace/{namespace_id}/", name="Get namespace", description="Get a specific namespace")
async def read_namespace(namespace_id: str):
    """Agent detail endpoint"""
    agent = prisma.agent.find_unique(where={"id": namespace_id}, include={"prompt": True})

    if agent:
        return {"success": True, "data": agent}

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Agent with id: {namespace_id} not found",
    )


@router.delete(
    "/namespace/{namespace_id}/", name="Delete namespace", description="Delete a specific namespace"
)
async def delete_agent(namespace_id: str):
    """Delete agent endpoint"""
    try:
        prisma.agentmemory.delete_many(where={"namespace_id": namespace_id})
        prisma.agent.delete(where={"id": namespace_id})

        return {"success": True, "data": None}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e,
        )


@router.patch(
    "/agent/{namespace_id}/", name="Patch namespace", description="Patch a specific namespace"
)
async def patch_namespace(namespace_id: str, body: dict):
    """Patch agent endpoint"""
    try:
        prisma.agent.update(data=body, where={"id": namespace_id})

        return {"success": True, "data": None}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e,
        )