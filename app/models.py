"""ORM models for the code archive."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from typing import List, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class File(Base):
    """A Python file that was indexed."""

    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)

    definitions: Mapped[List["Definition"]] = relationship(
        back_populates="file",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover - convenience only
        return f"File(id={self.id!r}, name={self.name!r})"


class Definition(Base):
    """A top-level or nested function/class discovered in a file."""

    __tablename__ = "definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    line_start: Mapped[int] = mapped_column(Integer, nullable=False)
    line_end: Mapped[int] = mapped_column(Integer, nullable=False)
    docstring: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    file: Mapped[File] = relationship(back_populates="definitions")

    def __repr__(self) -> str:  # pragma: no cover - convenience only
        return f"Definition(id={self.id!r}, name={self.name!r}, kind={self.kind!r})"
