"""Day 7-8: Todo CRUD 路由"""

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from api.deps import CurrentUser, SessionDep
from models import Todo, TodoCreate, TodoPublic

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", response_model=TodoPublic, status_code=status.HTTP_201_CREATED)
def create_todo(session: SessionDep, current_user: CurrentUser, todo_in: TodoCreate):
    todo = Todo(**todo_in.model_dump(), owner_id=current_user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@router.get("", response_model=list[TodoPublic])
def list_todos(session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 10):
    todos = session.exec(
        select(Todo).where(Todo.owner_id == current_user.id).offset(skip).limit(limit)
    ).all()
    return todos


@router.get("/{todo_id}", response_model=TodoPublic)
def get_todo(todo_id: int, session: SessionDep, current_user: CurrentUser):
    todo = session.get(Todo, todo_id)
    if not todo or todo.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, session: SessionDep, current_user: CurrentUser):
    todo = session.get(Todo, todo_id)
    if not todo or todo.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Todo not found")
    session.delete(todo)
    session.commit()
