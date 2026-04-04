#!/usr/bin/env python3

import uuid
import json
import datetime

from sqlalchemy import ForeignKey, Integer, String, Uuid, JSON, Boolean, Text, func, DateTime, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    login_name: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    login_name_in_use: Mapped[bool] = mapped_column(Boolean, default=False)


class Bot(Base):
    __tablename__ = 'bots'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    model_name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    prompt_template: Mapped[str] = mapped_column(Text().with_variant(LONGTEXT, "mysql"))


class Agreement(Base):
    __tablename__ = 'agreements'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(256), nullable=True)
    text: Mapped[str] = mapped_column(Text().with_variant(LONGTEXT, "mysql"))


class UserSignature(Base):
    __tablename__ = 'usersignatures'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    agreement_id: Mapped[int] = mapped_column(Integer, ForeignKey('agreements.id'))
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class UserSession(Base):
    __tablename__ = 'user_sessions'
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Instruction(Base):
    __tablename__ = 'instructions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(Text().with_variant(LONGTEXT, "mysql"))


class Task(Base):
    __tablename__ = 'tasks'
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    instruction_id: Mapped[int] = mapped_column(Integer, ForeignKey('instructions.id'))
    name: Mapped[str] = mapped_column(String(64), unique=True)
    public: Mapped[bool] = mapped_column(Boolean, default=False)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class UserTaskPermission(Base):
    __tablename__ = 'usertaskpermissions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    task_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey('tasks.id'))


class Prompt(Base):
    __tablename__ = 'prompts'
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    task_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey('tasks.id'))
    text: Mapped[str] = mapped_column(Text().with_variant(LONGTEXT, "mysql"))


class GenerationParams(Base):
    __tablename__ = 'generationparams'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    params: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class Generation(Base):
    __tablename__ = 'generations'
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    prompt_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey('prompts.id'))
    params_id: Mapped[int] = mapped_column(Integer, ForeignKey('generationparams.id'))
    text: Mapped[str] = mapped_column(Text().with_variant(LONGTEXT, "mysql"))


# Events
# We create Task Instance on display of the new prompt and generations to the user.
class TaskInstance(Base):
    __tablename__ = 'taskinstances'
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    prompt_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey('prompts.id'))
    generation_a_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey('generations.id'))
    generation_b_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey('generations.id'))
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class GenerationView(Base):
    # This table is redundant. It's prupose is to simplify selection.
    __tablename__ = 'generationviews'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    generation_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey('generations.id'))
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


# Clicks
class Vote(Base):
    __tablename__ = 'votes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    taskinstance_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey('taskinstances.id'))
    criterion: Mapped[str] = mapped_column(String(32), nullable=False)
    action_set: Mapped[bool] = mapped_column(Boolean, nullable=False)
    answer: Mapped[int] = mapped_column(Integer, nullable=False)
    # Normal votes: -3 -2 -1 0 +1 +2 +3
    #   negative values - generation A is better
    #   positive values - generation B is better
    #   zero            - genertaions are equal
    # -100 - both are equally bad
    # -200 - skip without voting
    # -300 - bad prompt
    # -400 - difficult to say
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Tag(Base):
    __tablename__ = 'tags'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    taskinstance_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey('taskinstances.id'))
    generation_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey('generations.id'))
    label: Mapped[str] = mapped_column(String(32), nullable=False)
    action_set: Mapped[bool] = mapped_column(Boolean, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


# Rating
class Rating(Base):
    __tablename__ = 'rating'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), primary_key=True)
    score: Mapped[float] = mapped_column(Float)


def normalize_json(data: dict) -> str:
    # Sort keys and remove whitespace to ensure consistent formatting
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


