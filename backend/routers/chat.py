"""Grounded chat using current Firestore summary; saves the conversation automatically."""
import os
from datetime import datetime, timezone
from uuid import uuid4
from typing import Annotated
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from backend.routers.data import read_summary, verify_admin, db
from backend.routers.conversations import Message

router = APIRouter(prefix='/api/chat', tags=['AI 채팅'])

class ChatInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = Field(default=None, max_length=100)

def talk_to_gpt(messages):
    from openai import OpenAI
    key=os.getenv('OPENAI_API_KEY','')
    if not key:raise HTTPException(503,'OPENAI_API_KEY가 설정되지 않았습니다.')
    model=os.getenv('OPENAI_MODEL','gpt-4o-mini')
    try:
        result=OpenAI(api_key=key, timeout=25.0, max_retries=1).chat.completions.create(
            model=model,messages=messages,max_completion_tokens=450)
        answer=result.choices[0].message.content
        if not answer:raise RuntimeError('Empty model response')
        return answer
    except Exception as exc:
        raise HTTPException(502,'AI 응답 생성에 실패했습니다. 서버 설정과 API 사용량을 확인하세요.') from exc

@router.post('')
def chat(body:ChatInput,x_admin_key:Annotated[str|None,Header()]=None):
    verify_admin(x_admin_key)
    summary=read_summary()
    system=(
        '당신은 이우성 선수 KBO 타격 기록을 설명하는 데이터 분석 비서입니다. '
        '다음 통계는 사용자의 Firestore 데이터에서 계산한 사실입니다. '\
        '통계 범위를 벗어나는 기록이나 특정 경기 수치를 지어내지 마세요. '\
        '요약에 없는 수치나 타율은 확인할 수 없다고 답하세요. '\
        'value는 경기별 안타 수이며 평균 안타 수는 타율이 아닙니다. '\
        f'\n[현재 데이터 요약]\n{summary}'
    )
    col=db().collection('conversations')
    past=[]
    if body.conversation_id:
        ref=col.document(body.conversation_id)
        doc=ref.get()
        if not doc.exists:raise HTTPException(404,'대화를 찾을 수 없습니다.')
        existing=doc.to_dict() or {}
        past=[Message.model_validate(x).model_dump() for x in existing.get('messages',[])]
        title=existing.get('title','새 대화')
    else:
        ref=col.document(str(uuid4()))
        title=body.message[:60]
    # Bound context and costs; retain all prior messages in DB (up to 40).
    if len(past)>=38:raise HTTPException(422,'대화가 길어졌습니다. 새 대화를 시작하세요.')
    user_msg={'role':'user','content':body.message}
    prompt=[{'role':'system','content':system}, *past[-12:], user_msg]
    answer=talk_to_gpt(prompt)
    messages=[*past,user_msg,{'role':'assistant','content':answer}]
    now=datetime.now(timezone.utc).isoformat()
    ref.set({'title':title,'messages':messages,'updated_at':now})
    return {'conversation_id':ref.id,'answer':answer,'summary':summary,'saved':True}
