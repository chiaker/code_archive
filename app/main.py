"""FastAPI application exposing the indexed code archive."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from . import crud, schemas
from .db import get_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure database tables exist before serving requests.

    This lets the API start (and return empty arrays) even if the indexer has
    not been run yet, instead of failing on a missing table.
    """

    init_db()
    yield


app = FastAPI(title="Code Archive API", lifespan=lifespan)


@app.get("/api/files", response_model=List[schemas.FileSummary])
def list_files(db: Session = Depends(get_db)) -> List[schemas.FileSummary]:
    """List all indexed files with the number of functions in each."""

    return [
        schemas.FileSummary(
            id=file.id,
            name=file.name,
            path=file.path,
            function_count=function_count,
        )
        for file, function_count in crud.list_files(db)
    ]
