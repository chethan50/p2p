import difflib, json
import streamlit as st
from src.config import data_dir,make_embeddings,make_llm
from src.db import documents,add_run
from src.vectorstore import store
from src.retrieval import retrieve,context_block
from src.chains import enhance,compare_answers,judge,DEFAULTS
from src.styles import STYLES
from src.render import result_card,citations
from src.exporter import as_json,as_markdown
st.title('Ask your documents'); st.caption('Turn a rough question into a well-scoped, evidence-backed analysis.')
active_ids=st.session_state.get('active_docs',[])
if active_ids:
  st.success(f"Ready to answer from {len(active_ids)} selected document(s). Type a question, then click **Enhance, compare, and judge**.")
else:
  st.warning('No documents are selected. Go to Workspace, select a document, then return here.')
task=st.selectbox('Task preset',list(DEFAULTS)); style=st.selectbox('Enhancement style',list(STYLES)); question=st.text_area('Your rough question',value=st.session_state.pop('reuse_prompt',''),placeholder='What matters here?')
st.caption('Try: What are the most important risks?  •  Which recommendations should we prioritize?')
rewrite_query=st.toggle('Let the enhancer rewrite the retrieval query',value=False)
if st.button('Enhance, compare, and judge',type='primary'):
  ids=active_ids
  if not ids: st.warning('Select documents in Workspace first.'); st.stop()
  try:
    with st.status('Working through the evidence…',expanded=True) as status:
      llm=make_llm(st.session_state.settings); ds=[d for d in documents(st.session_state.db) if d['id'] in ids]; preview=', '.join(d['name'] for d in ds)
      status.write('Enhancing prompt'); improved=enhance(llm,question,task,style,preview)
      status.write('Retrieving evidence'); vs=store(f'{data_dir()}/chroma',make_embeddings(st.session_state.settings)); docs=retrieve(vs,ids,improved.retrieval_query if rewrite_query else (question or DEFAULTS[task]),st.session_state.settings.top_k); context,sources=context_block(docs)
      if not docs: st.warning('No relevant context was retrieved.'); st.stop()
      status.write('Running original and enhanced prompts'); original,enhanced=compare_answers(llm,task,question or DEFAULTS[task],improved.enhanced_prompt,context)
      verdict=None
      if st.session_state.enable_judge:
        status.write('Blind judging'); verdict=judge(llm,question or DEFAULTS[task],context,original.model_dump_json(),enhanced.model_dump_json())
      status.update(label='Done',state='complete')
    st.session_state.last_run={'task':task,'style':style,'doc_ids':ids,'original_prompt':question or DEFAULTS[task],'enhanced_prompt':improved.enhanced_prompt,'original_response':original.model_dump_json(),'enhanced_response':enhanced.model_dump_json(),'judge_json':verdict.model_dump() if verdict else {},'provider':st.session_state.settings.provider,'model':st.session_state.settings.model,'sources':sources,'improvements':[x.model_dump() for x in improved.improvements]}
  except Exception as e: st.error(str(e))
run=st.session_state.get('last_run')
if run:
  c1,c2=st.columns(2); c1.subheader('Original prompt');c1.write(run['original_prompt']);c2.subheader('Enhanced prompt');c2.write(run['enhanced_prompt'])
  with st.expander('Prompt diff'): st.code('\n'.join(difflib.unified_diff(run['original_prompt'].splitlines(),run['enhanced_prompt'].splitlines(),lineterm='')))
  st.subheader('What changed and why'); st.table(run['improvements'])
  a,b=st.columns(2)
  with a: st.subheader('Original answer'); result_card(json.loads(run['original_response'])); citations(run['original_response'],run['sources'])
  with b: st.subheader('Enhanced answer'); result_card(json.loads(run['enhanced_response'])); citations(run['enhanced_response'],run['sources'])
  if run['judge_json']:
    st.subheader(f"Blind judge — winner: {run['judge_json']['winner']}"); st.dataframe([{k:v['original'], 'enhanced':v['enhanced'],'criterion':k,'why':v['justification']} for k,v in run['judge_json'].items() if isinstance(v,dict)],use_container_width=True)
  x,y,z=st.columns(3); x.download_button('Download Markdown',as_markdown(run),'run.md');y.download_button('Download JSON',as_json({k:v for k,v in run.items() if k!='sources'}),'run.json');
  if z.button('Save to library'): add_run(st.session_state.db,run); st.success('Saved to history.')
