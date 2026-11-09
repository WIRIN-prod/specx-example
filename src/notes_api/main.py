"""Notes API: receives requests, validates data, sends responses and errors."""

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, StringConstraints

from notes_api import store


@asynccontextmanager
async def lifespan(app: FastAPI):
    store.migrate()
    yield


app = FastAPI(title="Notes API", lifespan=lifespan)


@app.exception_handler(Exception)
async def internal_error(request: Request, exc: Exception) -> JSONResponse:
    # Starlette re-raises the error after this response, so uvicorn still logs it.
    return JSONResponse({"detail": "Internal Server Error"}, status_code=500)


Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Body = Annotated[str, Field(max_length=10000)]


class NoteIn(BaseModel):
    title: Title
    body: Body = ""


class NotePatch(BaseModel):
    # Pydantic does not validate defaults, so a missing field is None but an explicit null gets 422.
    title: Title = None
    body: Body = None


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


@app.get("/notes", response_model=list[Note])
def list_notes():
    return store.list_notes()


@app.patch("/notes/{id}", response_model=Note)
def update_note(id: int, patch: NotePatch):
    if patch.title is None and patch.body is None:
        raise HTTPException(status_code=422, detail="No fields to change")
    note = store.update_note(id, patch.title, patch.body)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.delete("/notes/{id}", status_code=204)
def delete_note(id: int):
    if not store.delete_note(id):
        raise HTTPException(status_code=404, detail="Note not found")
    return Response(status_code=204)
