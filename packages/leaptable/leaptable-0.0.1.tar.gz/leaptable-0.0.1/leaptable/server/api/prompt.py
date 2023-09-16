#!/usr/bin/env python

__authors__ = ["Peter W. Njenga"]
__copyright__ = "Copyright © 2023 Leaptable, Inc."

# Standard Libraries
from typing import Annotated

# External Libraries
import uuid

import requests
from loguru import logger
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Body, UploadFile, status
from pprint import pprint, pformat

# Internal Libraries
from reframe_api.server.lib.db_models.dataframe import Blueprint, DATA_TYPE, Dataframe, HistoryItem
from reframe_api.server.lib.security import get_user_token
from reframe_api.server.lib.db_models.user import User
from reframe_api.server.lib import hasura
from reframe_api.server.lib.util import flatten_prompt, extract_prompt_input_column_recursive

router = APIRouter()

@router.post("/prompt/run/")
async def dataframe_upload(request: Request, user: Annotated[User, Depends(get_user_token)], payload: dict = Body(...)):
    """Upload dataframe endpoint"""
    workspace_id = payload.get('workspace_id')
    dataframe_id = payload.get('dataframe_id')
    initiator_id = payload.get('initiator_id')
    prompt_version = payload.get('prompt_version')
    output_column_name = payload.get(f'output_column_name')
    output_column_slug = payload.get(f'output_column_slug')
    prompt = payload.get('prompt')

    try:
        limit = int(payload.get('limit', 10))
    except ValueError:
        if payload.get('limit').lower() == 'all':
            limit = None
            id_list = []
            logger.info(f"Processing all IDs")
        elif payload.get('limit').lower() == 'selected':
            limit = None
            id_list = payload.get('id_list', None)
            if id_list is None or len(id_list) == 0:
                logger.error(f"Selected ID list cannot be empty.")
                return {"error": "id_list cannot be empty."}, 400
            logger.debug(f"Processing selected ID list {len(id_list)}")
        else:
            logger.error(f"Invalid limit value {payload.get('limit')}")
            return {"error": "Invalid limit value"}, 400

    if output_column_name is None or output_column_slug is None:
        logger.error(f"Output column name and slug cannot be empty.")
        return {"error": "Output column name and slug cannot be empty."}, 400
    logger.info(
        f"Processing prompt {pformat(prompt)} with limit {limit} and output column [name={output_column_name} slug=({output_column_slug})]")

    workspace = await get_workspace(request, payload.get('workspace_id'))
    db_dataframe = await request.app.state.admin_db.fetch_one(
        "SELECT * FROM dataframe WHERE _id = (%(_id)s)", {'_id': dataframe_id}
    )
    dataframe = Dataframe(**db_dataframe)

    # Retrieve the column names
    column_name = None
    if prompt_version == 'v1.0':
        input_column = extract_prompt_input_column_recursive(prompt, trigger='@')
        agent_key = extract_prompt_input_column_recursive(prompt, trigger='/')
        prompt_text = flatten_prompt(prompt)
    else:
        for prompt_obj in request.json['prompt']:
            assert prompt_obj['type'] == 'paragraph'
            filt_mention = list(filter(lambda x: 'type' in x and x['type'] == 'mention', prompt_obj['children']))

            # If there is no column mentioned, skip.
            if len(filt_mention) == 0:
                continue

            column_name = filt_mention[0]['column']

    if input_column is None:
        raise HTTPException

    logger.info(f"Input column name: '{input_column}' → output column '{output_column_slug}'. Prompt: '{prompt_text}'")

    # Add new output columns to the database
    await workspace.data_db.execute(
        f"""
        ALTER TABLE {dataframe.table_name} ADD COLUMN IF NOT EXISTS {output_column_slug} jsonb default '{{}}'::jsonb;
        """
    )

    # Retrieve elements from the Client DB table for the Column Prompt.
    if limit is not None:
        sql_text_query = f"""
        SELECT _id, {input_column} FROM {dataframe.table_name}
        LIMIT {limit}
        """
    elif len(id_list) > 0:
        sql_text_query = f"""
            SELECT _id, {input_column} FROM {dataframe.table_name}
            WHERE _id IN ({', '.join(map(lambda i: f"'{str(i)}'", id_list))})
            """
    else:
        sql_text_query = f"""
        SELECT _id, {input_column} FROM {dataframe.table_name}
        """
    logger.debug(f"SQL Query: {sql_text_query}")


    res = requests.post(
        "http://100.101.28.98:8000/api/v1/agent/prompt/single_action_chat_agent/",
        json={
            'input_column': input_column,
            'prompt_text': prompt_text,
            'sql_query_text': sql_text_query,
            'output_column': output_column_slug,
            'table': dataframe.table_name,
            'initiator_id': initiator_id,
            'initiator_type': 'user-web',
        },
        headers={"X-API-KEY": workspace.framework_api_key}
    )

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.json())

    r_json = res.json()
    job_id = r_json['data']['id_']

    # Get the blueprint for the dataframe.
    db_blueprint = await request.app.state.admin_db.fetch_list(
        "SELECT * FROM blueprint WHERE dataframe_id = (%(dataframe_id)s)", {'dataframe_id': dataframe_id}
    )
    bp_list = [Blueprint(**bp) for bp in db_blueprint]

    column_exists = len(list(filter(lambda bp: bp.slug == output_column_slug, bp_list))) > 0

    if not column_exists:
        logger.debug(f"Adding column {output_column_slug} to blueprint.")
        # If the column add operation succeeded, proceed to add it to the table blueprint.
        new_bp = Blueprint(
            display_name=output_column_name,
            display_format=DATA_TYPE.TEXT,
            slug=output_column_slug,
            system=False,
            ai_gen=True,
            dataframe_id=dataframe_id,
            type=DATA_TYPE.JSONB,
        )


        await request.app.state.admin_db.execute(
            f"""
            INSERT INTO blueprint (_id, display_name, slug, display_format, dataframe_id, ai_gen, system, type)
            VALUES (%(id_)s, %(display_name)s, %(slug)s, %(display_format)s, %(dataframe_id)s, %(ai_gen)s, %(system)s, %(type)s)
            ON CONFLICT (dataframe_id, slug) DO NOTHING;
            """, new_bp.dict()
        )

    hist = HistoryItem(**{
        "item": {'prompt' : prompt},
        "version": "v1.01",
        "dataframe_id": dataframe_id,
        "workspace_id": workspace_id,
        "initiator_id": initiator_id,
        "job_id": job_id,
        "initiator_type": "user-web",
        "type": "PROMPT"
    })

    # Write the history item
    await request.app.state.admin_db.execute(
        """
        INSERT INTO history (_id, item, version, dataframe_id, workspace_id, initiator_id, job_id, initiator_type, type)
        VALUES (%(id_)s, %(item)s, %(version)s, %(dataframe_id)s, %(workspace_id)s, %(initiator_id)s, %(job_id)s, %(initiator_type)s, %(type)s);
        """, hist.dict()
    )

    # Reload the table metadata on Hasura
    res = hasura.reload_table_metadata(connection_name=workspace.hasura_params['data_db'], table_name=dataframe.table_name)


    return {"status": "success", "message": "Dataframe uploaded successfully"}

import json

from fastapi import APIRouter, Depends

from leaptable.server.lib.auth.prisma import JWTBearer, decodeJWT
from leaptable.server.lib.db_models.prompt import Prompt
from leaptable.server.lib.prisma import prisma

router = APIRouter()


@router.post("/prompts", name="Create a prompt", description="Create a new prompt")
async def create_prompt(body: Prompt):
    """Create prompt endpoint"""
    decoded = decodeJWT(token)

    prompt = prisma.prompt.create(
        {
            "name": body.name,
            "input_variables": json.dumps(body.input_variables),
            "template": body.template,
            "userId": decoded["userId"],
        },
        include={"user": True},
    )

    return {"success": True, "data": prompt}


@router.get("/prompts", name="List prompts", description="List all prompts")
async def read_prompts(token=Depends(JWTBearer())):
    """List prompts endpoint"""
    decoded = decodeJWT(token)
    prompts = prisma.prompt.find_many(
        where={"userId": decoded["userId"]},
        include={"user": True},
        order={"createdAt": "desc"},
    )

    return {"success": True, "data": prompts}


@router.get(
    "/prompts/{promptId}",
    name="Get prompt",
    description="Get a specific prompt",
)
async def read_prompt(promptId: str, token=Depends(JWTBearer())):
    """Get prompt endpoint"""
    prompt = prisma.prompt.find_unique(where={"id": promptId}, include={"user": True})

    return {"success": True, "data": prompt}


@router.delete(
    "/prompts/{promptId}",
    name="Delete prompt",
    description="Delete a specific prompt",
)
async def delete_prompt(promptId: str, token=Depends(JWTBearer())):
    """Delete prompt endpoint"""
    prisma.prompt.delete(where={"id": promptId})

    return {"success": True, "data": None}


@router.patch(
    "/prompts/{promptId}", name="Patch prompt", description="Patch a specific prompt"
)
async def patch_prompt(promptId: str, body: dict, token=Depends(JWTBearer())):
    """Patch prompt endpoint"""
    input_variables = body["input_variables"]
    if input_variables or input_variables == []:
        body["input_variables"] = json.dumps(input_variables)

    prompt = prisma.prompt.update(
        data=body,
        where={"id": promptId},
    )

    return {"success": True, "data": prompt}
