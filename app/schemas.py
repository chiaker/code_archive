"""Pydantic response schemas for the code archive API."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class DefinitionOut(BaseModel):
    """A single function or class definition as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    kind: str
    line_start: int
    line_end: int
    docstring: Optional[str] = None


class FileSummary(BaseModel):
    """A file entry with the number of functions it contains."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    path: str
    function_count: int


class FileStructureOut(BaseModel):
    """Full structure of a single file: all of its definitions."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    path: str
    definitions: List[DefinitionOut]


class SearchResult(BaseModel):
    """A definition matched by search, with its owning file."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    kind: str
    line_start: int
    line_end: int
    docstring: Optional[str] = None
    file_name: str
    file_path: str


class StatsOut(BaseModel):
    """Summary statistics for the whole archive."""

    files: int
    functions: int
    classes: int
    definitions: int
