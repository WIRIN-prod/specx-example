"""Notes API: receives requests, validates data, sends responses and errors."""

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, StringConstraints

from notes_api import store


@asynccontextmanager
async def lifespan(app: FastAPI):
    store.migrate()
    yield


app = FastAPI(title="Notes API", lifespan=lifespan)


class NoteIn(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
    body: Annotated[str, Field(max_length=10000)] = ""


class Note(BaseModel):
    id: int
    title: str
    body: str
    created_at: str
    updated_at: str


@app.post("/notes", status_code=201, response_model=Note)
def create_note(note: NoteIn):
    return store.create_note(note.title, note.body)


@app.get("/notes/{id}", response_model=Note)
def get_note(id: int):
    note = store.get_note(id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note
