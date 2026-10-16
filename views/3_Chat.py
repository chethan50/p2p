import streamlit as st
from src.db import chats,add_chat,messages,add_message
from src.config import data_dir,make_embeddings,make_llm
from src.vectorstore import store
from src.retrieval import retrieve,context_block
from src.chains import enhance,answer
from src.styles import STYLES
from src.render import citations
st.title('Chat with documents')
all_chats=chats(st.session_state.db)
if st.button('New chat') or not all_chats: st.session_state.chat_id=add_chat(st.session_state.db,'Document chat'); st.rerun()
chat_id=st.session_state.get('chat_id',all_chats[0]['id'] if all_chats else None)
for c in all_chats:
    if st.button(c['title'],key=f"chat{c['id']}"): st.session_state.chat_id=c['id'];st.rerun()
for msg in messages(st.session_state.db,chat_id):
    with st.chat_message(msg['role']): st.write(msg['content'])
question=st.chat_input('Ask a follow-up question')
if question:
  with st.chat_message('user'): st.write(question)
  add_message(st.session_state.db,chat_id,'user',question)
  try:
    ids=st.session_state.get('active_docs',[])
    llm=make_llm(st.session_state.settings); prompt=question
    do_enhance=st.toggle('Enhance each question',value=True,key='chat_enhance')
    enhanced=''
    if do_enhance: enhanced=enhance(llm,question,'Custom',st.selectbox('Style',list(STYLES),key='chatstyle'), 'selected documents').enhanced_prompt; prompt=enhanced
    docs=retrieve(store(f'{data_dir()}/chroma',make_embeddings(st.session_state.settings)),ids,question,st.session_state.settings.top_k); context,sources=context_block(docs); out=answer(llm,'Custom',prompt,context)
    with st.chat_message('assistant'):
      if enhanced:
        with st.expander('Enhanced prompt'): st.write(enhanced)
      st.markdown(out.answer); citations(out.answer,sources)
    add_message(st.session_state.db,chat_id,'assistant',out.answer,enhanced)
  except Exception as e: st.error(str(e))
