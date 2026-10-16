import streamlit as st
from src.db import documents
from src.config import data_dir,make_embeddings,make_llm
from src.vectorstore import store
from src.retrieval import retrieve,context_block
from src.chains import conflicts
st.title('Compare documents')
rows=documents(st.session_state.db); ids=st.multiselect('Choose 2–5 documents',[r['id'] for r in rows],format_func=lambda x:next(r['name'] for r in rows if r['id']==x),max_selections=5); topic=st.text_input('Focus topic (optional)')
if st.button('Detect agreements and conflicts',type='primary'):
  if len(ids)<2: st.warning('Choose at least two documents.');st.stop()
  try:
    vs=store(f'{data_dir()}/chroma',make_embeddings(st.session_state.settings)); blocks=[]
    for did in ids:
      d=next(x for x in rows if x['id']==did); docs=retrieve(vs,[did],topic or 'key claims facts numbers dates',st.session_state.settings.top_k); context,_=context_block(docs); blocks.append(f"DOCUMENT {d['name']} ({did}):\n{context}")
    report=conflicts(make_llm(st.session_state.settings),topic,'\n\n'.join(blocks)); st.session_state.conflict=report
  except Exception as e: st.error(str(e))
if report:=st.session_state.get('conflict'):
  counts={x:sum(t.status==x for t in report.topics) for x in ['agree','conflict','unique']}; a,b,c=st.columns(3);a.metric('Agreements',counts['agree']);b.metric('Conflicts',counts['conflict']);c.metric('Unique points',counts['unique'])
  for item in report.topics:
    with st.expander(f"{item.status.upper()} · {item.topic} ({item.severity})",expanded=True): st.write(item.explanation);st.table([p.model_dump() for p in item.positions])
