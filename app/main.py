"""FastAPI application exposing the indexed code archive."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query
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


@app.get("/api/files/{name}/structure", response_model=schemas.FileStructureOut)
def file_structure(name: str, db: Session = Depends(get_db)) -> schemas.FileStructureOut:
    """Return the full structure (functions and classes) of one file.

    A missing file is a 404 (not found); a file with no definitions returns an
    empty ``definitions`` list rather than an error.
    """

    file = crud.get_file_structure(db, name)
    if file is None:
        raise HTTPException(status_code=404, detail=f"File not found: {name}")

    return schemas.FileStructureOut(
        name=file.name,
        path=file.path,
        definitions=[schemas.DefinitionOut.model_validate(d) for d in file.definitions],
    )


@app.get("/api/search", response_model=List[schemas.SearchResult])
def search(
    q: str = Query(..., description="Keyword to match in a name or docstring"),
    db: Session = Depends(get_db),
) -> List[schemas.SearchResult]:
    """Search definitions by name or docstring (case-insensitive).

    Returns an empty list when nothing matches (never a 500).
    """

    return [
        schemas.SearchResult(
            id=d.id,
            name=d.name,
            kind=d.kind,
            line_start=d.line_start,
            line_end=d.line_end,
            docstring=d.docstring,
            file_name=d.file.name,
            file_path=d.file.path,
        )
        for d in crud.search_definitions(db, q)
    ]
