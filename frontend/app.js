'use strict';
const API = String(window.API_BASE_URL || '').replace(/\/$/, '');
const $ = id => document.getElementById(id);
let conversationId = null;
let records = [];
let busy = false;
// The admin key is stored only for this browser tab session, not in source code.
const ADMIN_KEY_SESSION_NAME = 'lee-woosung-scout-admin-key';
function restoreAdminKey(){
  try { $('key').value = sessionStorage.getItem(ADMIN_KEY_SESSION_NAME) || ''; }
  catch { /* Storage may be disabled; manual entry still works. */ }
}
function rememberAdminKey(){
  try { sessionStorage.setItem(ADMIN_KEY_SESSION_NAME, key()); }
  catch { /* Continue without session persistence when storage is unavailable. */ }
}
function forgetAdminKey(){
  try { sessionStorage.removeItem(ADMIN_KEY_SESSION_NAME); }
  catch { /* Clearing the visible field still works. */ }
}
restoreAdminKey();
$('api-label').textContent = 'API: ' + API;
function key(){return $('key').value.trim();}
function err(msg){$('global-error').hidden=!msg; $('global-error').textContent=msg||'';}
function status(ok,msg){$('status-dot').classList.toggle('good',ok);$('status').textContent=msg;}
async function api(path, options={}){
  const headers={'Accept':'application/json'};
  if(options.body) headers['Content-Type']='application/json';
  if(options.auth!==false){if(!key())throw new Error('먼저 관리자 키를 입력하세요.');headers['x-admin-key']=key();}
  const res=await fetch(API+path,{method:options.method||'GET',headers,body:options.body?JSON.stringify(options.body):undefined});
  let data;try{data=await res.json();}catch{data={};}
  if(!res.ok)throw new Error(res.status+' 오류: '+(typeof data.detail==='string'?data.detail:'요청을 처리할 수 없습니다.'));
  return data;
}
function fmt(n,digits=2){return typeof n==='number'?n.toLocaleString('ko-KR',{maximumFractionDigits:digits}):'—';}
async function summary(){const s=await api('/api/data/summary',{auth:false});$('stat-count').textContent=fmt(s.count,0);$('stat-total').textContent=fmt(s.metrics?.total,0);$('stat-avg').textContent=fmt(s.metrics?.average,3);$('stat-trend').textContent=s.trend||'—';$('period').textContent=s.period?`기간: ${s.period.start} ~ ${s.period.end} · 평균 안타 수는 타율이 아닙니다.`:'데이터가 없습니다.';}
function bubble(role,content){const el=document.createElement('div');el.className='bubble '+role;el.textContent=content;$('messages').appendChild(el);$('messages').scrollTop=$('messages').scrollHeight;}
function renderMessages(messages){$('messages').replaceChildren();for(const m of messages)bubble(m.role,m.content);}
async function history(){const data=await api('/api/conversations');const list=$('history-list');list.replaceChildren();if(!data.conversations?.length){const li=document.createElement('li');li.textContent='대화 기록 없음';list.append(li);return;}for(const row of data.conversations){const li=document.createElement('li');const btn=document.createElement('button');btn.type='button';btn.textContent=row.title||'새 대화';const sub=document.createElement('small');sub.textContent=`${row.message_count}개 메시지 · ${row.updated_at||''}`;btn.append(sub);btn.onclick=async()=>{try{err('');const d=await api('/api/conversations/'+encodeURIComponent(row.id));conversationId=d.id;renderMessages(d.messages||[]);}catch(e){err(e.message);}};const del=document.createElement('button');del.type='button';del.textContent='대화 삭제';del.className='history-delete';del.setAttribute('aria-label','대화 삭제: '+(row.title||'새 대화'));del.onclick=async()=>{if(!confirm('이 대화 기록을 삭제할까요? 삭제 후 복구할 수 없습니다.'))return;try{err('');await api('/api/conversations/'+encodeURIComponent(row.id),{method:'DELETE'});if(conversationId===row.id){conversationId=null;$('messages').replaceChildren();const p=document.createElement('p');p.className='muted';p.textContent='삭제한 대화입니다. 새 질문을 입력하세요.';$('messages').append(p);}await history();}catch(e){err(e.message);}};li.append(btn,del);list.append(li);}}
async function loadRecords(){const data=await api('/api/data?limit=105',{auth:false});records=data.records||[];const tbody=$('rows');tbody.replaceChildren();if(!records.length){const tr=document.createElement('tr');const td=document.createElement('td');td.colSpan=4;td.textContent='데이터 없음';tr.append(td);tbody.append(tr);return;}for(const r of records){const tr=document.createElement('tr');for(const val of [r.date,fmt(r.value),r.memo||'']){const td=document.createElement('td');td.textContent=val;tr.append(td);}const td=document.createElement('td');const edit=document.createElement('button');edit.type='button';edit.textContent='수정';edit.className='secondary';edit.onclick=()=>{$('record-id').value=r.id;$('date').value=r.date;$('value').value=r.value;$('memo').value=r.memo||'';$('save-record').textContent='수정 저장';$('cancel-edit').hidden=false;$('data-form').scrollIntoView({behavior:'smooth',block:'center'});};const del=document.createElement('button');del.type='button';del.textContent='삭제';del.className='delete';del.onclick=async()=>{if(!confirm(`${r.date} 기록을 삭제할까요? 복구할 수 없습니다.`))return;try{await api('/api/data/'+encodeURIComponent(r.id),{method:'DELETE'});$('data-feedback').textContent='삭제 완료';await Promise.all([loadRecords(),summary()]);}catch(e){err(e.message);}};td.append(edit,del);tr.append(td);tbody.append(tr);}}
function resetEdit(){$('data-form').reset();$('record-id').value='';$('save-record').textContent='데이터 추가';$('cancel-edit').hidden=true;}
$('connect').onclick=async()=>{try{err('');await api('/api/conversations');rememberAdminKey();status(true,'API 인증 성공 · 현재 탭에 키 유지');await Promise.all([history(),summary(),loadRecords()]);}catch(e){if(e.message.startsWith('401')||e.message.startsWith('403'))forgetAdminKey();status(false,'연결 또는 인증 실패');err(e.message);}};
$('clear-key').onclick=()=>{forgetAdminKey();$('key').value='';conversationId=null;status(false,'키 입력 필요');$('history-list').replaceChildren();};
$('new-chat').onclick=()=>{conversationId=null;$('messages').replaceChildren();const p=document.createElement('p');p.className='muted';p.textContent='새 대화를 시작합니다.';$('messages').append(p);};
$('reload-history').onclick=()=>history().catch(e=>err(e.message));
$('reload-data').onclick=()=>Promise.all([loadRecords(),summary()]).catch(e=>err(e.message));
$('cancel-edit').onclick=resetEdit;
$('chat-form').onsubmit=async e=>{e.preventDefault();if(busy)return;const message=$('message').value.trim();if(!message)return;busy=true;err('');$('send').disabled=true;$('chat-progress').hidden=false;try{if($('messages').querySelector('.muted'))$('messages').replaceChildren();bubble('user',message);$('message').value='';const res=await api('/api/chat',{method:'POST',body:{message,conversation_id:conversationId}});conversationId=res.conversation_id;bubble('assistant',res.answer||'답변 내용 없음');await history();}catch(ex){err(ex.message);bubble('assistant','요청이 완료되지 않았습니다. 오류 메시지를 확인하세요.');}finally{busy=false;$('send').disabled=false;$('chat-progress').hidden=true;}};
$('data-form').onsubmit=async e=>{e.preventDefault();err('');const id=$('record-id').value;const val=Number($('value').value);if(!Number.isFinite(val))return err('올바른 안타 수를 입력하세요.');const payload={date:$('date').value,value:val,memo:$('memo').value.trim()};try{await api(id?'/api/data/'+encodeURIComponent(id):'/api/data',{method:id?'PUT':'POST',body:payload});$('data-feedback').textContent=id?'수정 완료':'추가 완료';resetEdit();await Promise.all([loadRecords(),summary()]);}catch(ex){err(ex.message);}};
Promise.all([summary(),loadRecords()]).then(()=>{
  if(key()) $('connect').click(); // Restore the tab session after a refresh.
  else status(false,'데이터 조회 성공 · 인증 필요');
}).catch(e=>{status(false,'연결 확인 필요');err(e.message);});
