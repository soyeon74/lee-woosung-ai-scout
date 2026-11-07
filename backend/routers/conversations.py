"""Conversation storage with explicit message retrieval."""
from datetime import datetime, timezone
from uuid import uuid4
from typing import Annotated, Literal
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from backend.routers.data import verify_admin, db

router = APIRouter(prefix='/api/conversations', tags=['대화 기록'])

class Message(BaseModel):
    model_config = ConfigDict(extra='forbid')
    role: Literal['user', 'assistant']
    content: str = Field(min_length=1, max_length=5000)

class ConversationInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str = Field(default='새 대화', min_length=1, max_length=120)
    messages: list[Message] = Field(min_length=1, max_length=40)

def safe_conversation(doc):
    raw = doc.to_dict() or {}
    return {'id':doc.id, 'title':raw.get('title','새 대화'), 'messages':raw.get('messages',[]), 'updated_at':raw.get('updated_at')}

@router.post('', status_code=201)
def save_conversation(body:ConversationInput, x_admin_key:Annotated[str|None,Header()]=None):
    verify_admin(x_admin_key)
    now=datetime.now(timezone.utc).isoformat()
    ref=db().collection('conversations').document(str(uuid4()))
    item={'title':body.title,'messages':[m.model_dump() for m in body.messages],'updated_at':now}
    ref.set(item)
    return {'id':ref.id,**item}

@router.get('')
def list_conversations(x_admin_key:Annotated[str|None,Header()]=None):
    verify_admin(x_admin_key)
    items=[]
    for doc in db().collection('conversations').stream():
        row=safe_conversation(doc)
        items.append({'id':row['id'],'title':row['title'],'updated_at':row['updated_at'], 'message_count':len(row['messages'])})
    items.sort(key=lambda x:x.get('updated_at') or '',reverse=True)
    return {'count':len(items),'conversations':items[:100]}

@router.get('/{id}')
def get_conversation(id:str,x_admin_key:Annotated[str|None,Header()]=None):
    verify_admin(x_admin_key)
    doc=db().collection('conversations').document(id).get()
    if not doc.exists:raise HTTPException(404,'대화를 찾을 수 없습니다.')
    return safe_conversation(doc)

@router.delete('/{id}')
def delete_conversation(id:str,x_admin_key:Annotated[str|None,Header()]=None):
    verify_admin(x_admin_key)
    ref=db().collection('conversations').document(id)
    if not ref.get().exists:raise HTTPException(404,'대화를 찾을 수 없습니다.')
    ref.delete()
    return {'id':id,'deleted':True}
