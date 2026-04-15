#!/usr/bin/env python3

import json

from typing import List
from .models import Tag as TagModel  # Rename to avoid confusion
from pydantic import BaseModel
from pydantic.types import Json
from uuid import UUID

from fastapi import FastAPI, Request, Response, Depends, Cookie, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .service import DataCollectionPlatform


app = FastAPI(title="Crowdsourcing")


# Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",  # Frontend development server
#         "http://localhost:8000",  # Backend when serving frontend
#         "http://127.0.0.1:3000",
#         "http://127.0.0.1:8000",
#     ],  # Be explicit about allowed origins for cookies to work properly
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods
#     allow_headers=["*"],  # Allows all headers
#     expose_headers=["Content-Type", "Set-Cookie"],
# )


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/home")
def home(
    request: Request,
    response: Response,
    session_id: str = Cookie(None),
    db: Session = Depends(get_db),
):
    srv = DataCollectionPlatform()

    user_id = None
    if session_id:
        try:
            user_id = srv.get_user_id(db, session_id)
        except Exception:
            # Invalid session ID format (e.g., not a UUID)
            user_id = None

    if session_id is None or user_id is None:
        session_id, user_id = srv.add_user(db)
        # Set cookie with minimal restrictions for testing
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=60 * 60 * 24 * 365 * 2,  # 2 years
            httponly=False,  # Allow JavaScript access for debugging
            #samesite="none",  # Allow cross-site requests
            path="/",
            #secure=False,  # Disable for non-HTTPS development environments
        )

    print(session_id)
    return {
        "session_id": session_id
    }


def _get_user_id(db: Session, session_id: str):
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No session id"
        )

    srv = DataCollectionPlatform()

    # Check if user ID is valid
    try:
        user_id = srv.get_user_id(db, session_id)
    except Exception:
        # Invalid session ID format (e.g., not a UUID)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session"
        )

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session"
        )

    return srv, user_id


@app.get("/tasks")
def tasks(
    request: Request,
    response: Response,
    session_id: str = Cookie(None),
    db: Session = Depends(get_db),
):
    srv, user_id = _get_user_id(db, session_id)

    user_tasks = srv.get_tasks_for_user(db, user_id)
    return {
        "session_id": session_id,
        "tasks": user_tasks
    }


class NextGeneration(BaseModel):
    id: UUID
    text: str


class NextTask(BaseModel):
    meta: str
    prompt: str
    task_instance_id: UUID
    generations: List[NextGeneration]


class DefaultRequest(BaseModel):
    pass


@app.post("/task/{task_id}/next")
def task(
    request: Request,
    response: Response,
    task_id: str,
    session_id: str = Cookie(None),
    db: Session = Depends(get_db),
):
    srv, user_id = _get_user_id(db, session_id)

    user_tasks = srv.get_tasks_for_user(db, user_id)  # check if this task is allowed
    print(user_tasks)
    if str(task_id) not in [str(v["id"]) for v in user_tasks]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unknown task id"
        )
    task = srv.get_task_by_id(db, task_id)
    task_instance = srv.get_task_instance_for_user(db, task_id, user_id)

    # Convert UUIDs to strings to match the expected response model
    meta = task["meta"]
    if isinstance(meta, dict):
        meta = json.dumps(meta)

    return {
        "meta": meta,
        "prompt": task_instance["prompt"],
        "task_instance_id": str(task_instance["id"]),
        "generations": [
            {
                "id": str(task_instance["generations"][0]["id"]),
                "text": task_instance["generations"][0]["text"],
            },
            {
                "id": str(task_instance["generations"][1]["id"]),
                "text": task_instance["generations"][1]["text"],
            },
        ],
    }


@app.get("/task/{task_id}/instruction")
def get_task_instruction(task_id: UUID, db: Session = Depends(get_db)):
    srv = DataCollectionPlatform()
    return srv.get_instruction_for_task(db, task_id)


class Vote(BaseModel):
    task_instance_id: UUID
    generation_a_id: UUID
    generation_b_id: UUID
    action: bool # true for set, false for clear
    criterion: str
    value: int


@app.post("/task/vote")
def vote(vote: Vote, session_id: str = Cookie(None), db: Session = Depends(get_db)):
    srv, _ = _get_user_id(db, session_id)

    srv.add_vote(
        db,
        vote.task_instance_id,
        vote.generation_a_id,
        vote.generation_b_id,
        vote.action,
        vote.criterion,
        vote.value,
    )

    return {}


class TagRequest(BaseModel):
    task_instance_id: UUID
    generation_id: UUID
    action: bool  # true for set, false for clear
    tag: str


@app.post("/task/tag")
def tag(tag: TagRequest, session_id: str = Cookie(None), db: Session = Depends(get_db)):
    srv, _ = _get_user_id(db, session_id)

    srv.add_tag(
        db,
        tag.task_instance_id,
        tag.generation_id,
        tag.action,
        tag.tag
    )

    return {}


@app.get("/user/agreements")
def user_agreements_status(
    session_id: str = Cookie(None), db: Session = Depends(get_db)
):
    srv, user_id = _get_user_id(db, session_id)

    # Get agreements
    try:
        agreements = srv.get_agreements_for_user(db, session_id)
        return agreements
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/agreement")
def get_agreement_text(agreement_id: int, db: Session = Depends(get_db)):
    srv = DataCollectionPlatform()
    res = srv.get_agreement_text(db, agreement_id)
    return res


@app.post("/user/sign")
def user_agreement_sign(
    agreement_id: int, session_id: str = Cookie(None), db: Session = Depends(get_db)
):
    srv, user_id = _get_user_id(db, session_id)

    # Record the agreement
    try:
        signature = srv.record_agreement(db, session_id, agreement_id)

        # Get updated agreements for the user
        agreements = srv.get_agreements_for_user(db, session_id)

        return {
            "success": True,
            "agreements": agreements
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


class BotParameters(BaseModel):
    model_name: str
    prompt_template: str
    config: Json[dict]


@app.post("/create_bot_session")
def create_bot_session(params: BotParameters, db: Session = Depends(get_db)):
    srv = DataCollectionPlatform()
    session_id = srv.create_bot_session(
        db, params.model_name, params.prompt_template, params.config
    )
    return {
        "session_id": session_id
    }


@app.get("/stat/votes/total")
def get_total_votes(db: Session = Depends(get_db)):
    srv = DataCollectionPlatform()
    return {
        'count': srv.get_total_votes(db)
    }


@app.get("/stat/rating")
def get_rating(start: int = None, count: int = 10, session_id: str = Cookie(None), db: Session = Depends(get_db)):
    srv = DataCollectionPlatform()
    user_id = None
    if session_id is not None:
        user_id = srv.get_user_id(db, session_id)

    return srv.get_rating(db, user_id, start, count)


import os

# Determine the public directory path - works in both Docker and local development
# In Docker: /app/public (frontend built files)
# In local dev: ../public relative to this file (back/app/public)
public_dir = "/app/public" if os.path.exists("/app/public") else os.path.join(os.path.dirname(__file__), "public")
app.mount("/", StaticFiles(directory=public_dir, html=True), name="public")
