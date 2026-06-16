"""FastAPI application exposing the indexed code archive."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure database tables exist before serving requests.

    This lets the API start (and return empty arrays) even if the indexer has
    not been run yet, instead of failing on a missing table.
    """

    init_db()
    yield


app = FastAPI(title="Code Archive API", lifespan=lifespan)
