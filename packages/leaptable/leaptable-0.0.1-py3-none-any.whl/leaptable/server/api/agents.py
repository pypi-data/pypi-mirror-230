#!/usr/bin/env python

__authors__ = ["Peter W. Njenga"]
__copyright__ = "Copyright © 2023 Leaptable, Inc."

# Standard Libraries
import json
from pprint import pprint, pformat
from time import time

# External Libraries
from psycopg import sql
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, Optional
from loguru import logger

from leaptable.server.lib.db_connection import Database
from leaptable.server.lib.db_models.namespace import Namespace, Job, PROCESSING_STATUS
# from leaptable.server.lib.auth.prisma import JWTBearer, decodeJWT
from leaptable.server.lib.db_models.agent import Agent
# from leaptable.server.lib.prisma import prisma

router = APIRouter()
from os import environ as os_env
import os
import redis
REDIS_STREAM_HOST=os.environ.get('REDIS_STREAM_HOST', "localhost")
REDIS_PASSWORD=os.environ.get('REDIS_PASSWORD')
red_stream = redis.StrictRedis(
    REDIS_STREAM_HOST, 6379, charset="utf-8",
    password=REDIS_PASSWORD, decode_responses=True)

from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader


api_key_header = APIKeyHeader(name="X-API-KEY")
async def get_api_key(request: Request, api_key_header: str = Security(api_key_header)) -> str:

    # Check the API key
    db_api_key = await request.app.state.meta_db.fetch_one(
        """SELECT * FROM API_KEY WHERE key = %(key)s""",
        {'key': api_key_header})
    if db_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )

    try:
        namespace_id = db_api_key['namespace_id']
        # Update the usage count
        await request.app.state.meta_db.execute(
            """UPDATE api_key 
                   SET usage_count = usage_count + 1
                WHERE _id = %(_id)s;
            """, {'_id': db_api_key['_id']})

        # Get the namespace
        db_namespace = await request.app.state.meta_db.fetch_one(
            """SELECT * FROM namespace WHERE _id = %(_id)s""",
            {'_id': namespace_id})

        print(api_key_header, namespace_id, db_namespace)

        # Connect to the namespace and create the trace schema
        if namespace_id not in request.app.state.trace_db:
            trace_db = Database(**json.loads(db_namespace['trace_db_params']))
            await trace_db.connect()

            request.app.state.trace_db[namespace_id] = trace_db
            logger.info(f"Created new connection to namespace trace_db {trace_db}")

        if namespace_id not in request.app.state.data_db:
            data_db = Database(**json.loads(db_namespace['data_db_params']))
            await data_db.connect()

            request.app.state.data_db[namespace_id] = data_db
            logger.info(f"Created new connection to namespace data_db {data_db}")

        logger.info(f"Using namespace->{db_namespace['slug']} ({db_namespace['name']})")

        ns ={
            **db_namespace,
            'trace_db': request.app.state.trace_db[namespace_id],
            'data_db': request.app.state.data_db[namespace_id],
            'trace_db_params': {},
            'data_db_params': {}
        }
        return Namespace(**ns)

    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@router.post("/agent/", name="Create agent", description="Create a new agent")
async def create_agent(body: Agent):
    """Agents endpoint"""
    try:
        agent = prisma.agent.create(
            {
                "name": body.name,
                "type": body.type,
                "llm": json.dumps(body.llm),
                "hasMemory": body.hasMemory,
                "userId": decoded["userId"],
                "promptId": body.promptId,
            },
            include={"user": True},
        )

        return {"success": True, "data": agent}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e,
        )


@router.get("/agent", name="List all agents", description="List all agents")
async def read_agents():
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


@router.get("/agent/{agentId}", name="Get agent", description="Get a specific agent")
async def read_agent(agentId: str):
    """Agent detail endpoint"""
    agent = prisma.agent.find_unique(where={"id": agentId}, include={"prompt": True})

    if agent:
        return {"success": True, "data": agent}

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Agent with id: {agentId} not found",
    )


@router.delete(
    "/agent/{agentId}", name="Delete agent", description="Delete a specific agent"
)
async def delete_agent(agentId: str):
    """Delete agent endpoint"""
    try:
        prisma.agentmemory.delete_many(where={"agentId": agentId})
        prisma.agent.delete(where={"id": agentId})

        return {"success": True, "data": None}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e,
        )


@router.patch(
    "/agent/{agentId}", name="Patch agent", description="Patch a specific agent"
)
async def patch_agent(agentId: str, body: dict):
    """Patch agent endpoint"""
    try:
        prisma.agent.update(data=body, where={"id": agentId})

        return {"success": True, "data": None}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e,
        )


@router.post(
    "/agent/prompt/single_action_chat_agent/",
    name="Prompt agent",
    description="Invoke a single action chat agent",
)
async def single_action_chat_agent(
    request: Request,
    body: dict,
    namespace: Annotated[Namespace, Depends(get_api_key)]
):

    """Agent detail endpoint"""
    sql_query_text = body.get("sql_query_text")
    table_name = body.get("table")
    output_column = body.get("output_column")
    initiator_id = body.get("initiator_id")
    initiator_type = body.get("initiator_type")
    prompt = body.get("prompt")
    prompt_text = body.get("prompt_text")
    input_column = body.get("input_column")

    logger.debug(f"Prompt text: '{prompt_text}' Input column: '{input_column}' Output column: '{output_column}' sql_query_text: '{sql_query_text}'")

    job = Job(
        prompt=json.dumps(prompt),
        prompt_format_version="v0.0.1",
        initiator_id=initiator_id,
        initiator_type=initiator_type,
        read_cache=True,
        write_cache=True,
        table_name=table_name,
        input_params=json.dumps({
            "sql_query_text": sql_query_text,
            "input_column": input_column,
        }),
        output_params=json.dumps({
            "output_column": output_column,
        })
    )

    try:
        await namespace.trace_db.execute(
            """
            INSERT INTO trace.job (_id, prompt, table_name, prompt_format_version, initiator_id, initiator_type,
                        read_cache, write_cache, input_params, output_params)
            VALUES (%(id_)s, %(prompt)s, %(table_name)s,%(prompt_format_version)s, %(initiator_id)s, %(initiator_type)s,
                        %(read_cache)s, %(write_cache)s, %(input_params)s, %(output_params)s)
            """, job.dict())
        logger.info(f"Added job to DB {job.id_}")

    except Exception as e:
        logger.exception(e)

    # Determine agent type
    is_browser_agent = False
    is_serp_agent = False
    activation_command = None
    for key_word in ["browse", "visit"]:
        if f"/{key_word}" in prompt_text:
            is_browser_agent = True
            activation_command = f"/{key_word}"
            logger.debug(f"Activation command: {activation_command}")
            break

    for key_word in ["google_search", "search_google", "google", "search"]:
        if f"/{key_word}" in prompt_text:
            is_serp_agent = True
            activation_command = f"/{key_word}"
            logger.debug(f"Activation command: {activation_command}")
            break

    if is_browser_agent:
        stream_key = "leaptable::instream::agent->browser"
    elif is_serp_agent:
        stream_key = "leaptable::instream::agent->serp"
    else:
        raise Exception("Unknown agent type")

    logger.debug(f"Stream key: {stream_key}")

    # Fetch items from DB and add to stream
    items = await namespace.data_db.fetch_list(
        sql_query_text, {})

    record_count = 0
    for record in items:

        if is_browser_agent:
            payload = {
                "_id": str(record['_id']),
                "url": record[input_column]
            }
        elif is_serp_agent:
            serp_query = prompt_text.split(("."))[0].replace(activation_command, "")
            serp_query = serp_query.replace(f"@{input_column}", record[1])
            serp_query = serp_query.strip()

            payload = {
                "_id": str(record['_id']),
                "query": serp_query
            }
        else:
            raise Exception("Unknown agent type")

        stream_message = {
            'ts': time(),
            'payload': json.dumps(payload),
            'job_id': str(job.id_),
            'namespace_id': str(namespace.id_),
            "table_name": table_name,
            "prompt": json.dumps(prompt),
            "prompt_text": prompt_text,
            "output_column": output_column,
        }

        # Update status to QUEUED
        item = await namespace.data_db.fetch_one(
            f'SELECT * FROM {table_name} WHERE _id = %(_id)s', {'_id': record['_id']})
        elem = json.loads(item[output_column])
        elem['status'] = PROCESSING_STATUS.QUEUED.value
        item = await namespace.data_db.execute(
            f'UPDATE {table_name} SET {output_column} = %(elem)s WHERE _id = %(_id)s',
            {'_id': record['_id'], 'elem': json.dumps(elem)})

        red_stream.xadd(stream_key, stream_message)
        logger.opt(ansi=True).debug(f"Added elem to stream <b>{stream_key}</b>. Elem: <green>{pformat(stream_message)}</green>")
        record_count += 1
    logger.info(f"Added {record_count} elems to stream {stream_key}")

    return {"status": "success", 'data': job.dict()}