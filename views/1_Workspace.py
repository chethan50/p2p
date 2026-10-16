import uuid, os
import streamlit as st
from src.config import data_dir,make_embeddings
from src.db import add_document,documents,delete_document
from src.ingestion import extract_upload
from src.vectorstore import store,page_chunks,add_documents,delete_document as delete_vectors
st.title('Document workspace'); st.caption('Bring your PDFs, text files, and notes into one evidence-grounded workspace.')
uploads=st.file_uploader('Upload PDF, TXT, or Markdown',type=['pdf','txt','md'],accept_multiple_files=True)
text=st.text_area('Or paste text'); title=st.text_input('Pasted-text title',value='Untitled note')
if st.button('Ingest documents',type='primary'):
    items=[(f.name,f.getvalue()) for f in (uploads or [])]+([(title,text.encode())] if text.strip() else [])
    if not items: st.warning('Choose a file or paste some text.')
    else:
      try:
        with st.status('Extracting and embedding documents…',expanded=True) as status:
          emb=make_embeddings(st.session_state.settings); vs=store(f'{data_dir()}/chroma',emb)
          known={d['content_hash'] for d in documents(st.session_state.db)}
          ingested_ids=[]
          for name,data in items:
            doc=extract_upload(name,data)
            if doc.content_hash in known: st.write(f'Already indexed: {name}'); continue
            did=str(uuid.uuid4()); add_documents(vs,page_chunks(did,name,doc.pages,st.session_state.settings.chunk_size),did)
            add_document(st.session_state.db,{'id':did,'name':name,'content_hash':doc.content_hash,'pages':len(doc.pages),'words':doc.words,'tokens':doc.tokens})
            ingested_ids.append(did)
            st.write(f'Indexed {name}: {len(doc.pages)} pages, {doc.words:,} words')
          status.update(label='Ingestion complete',state='complete')
        if ingested_ids:
          st.session_state.active_docs=ingested_ids
          st.success(f"{len(ingested_ids)} document(s) are ready. They are selected for questions below.")
      except Exception as e: st.error(str(e))
rows=documents(st.session_state.db)
if rows:
    st.subheader('Documents')
    active=st.multiselect('Active documents',[r['id'] for r in rows],default=st.session_state.get('active_docs',[r['id'] for r in rows]),format_func=lambda x:next(r['name'] for r in rows if r['id']==x))
    st.session_state.active_docs=active
    if active:
        if st.button('Next: ask questions about selected documents',type='primary'):
            st.switch_page('views/2_Ask.py')
    else:
        st.info('Select at least one document above before asking a question.')
    st.dataframe([{k:v for k,v in r.items() if k!='content_hash'} for r in rows],use_container_width=True)
    remove=st.selectbox('Delete document',[None]+[r['id'] for r in rows],format_func=lambda x:'Choose a document' if not x else next(r['name'] for r in rows if r['id']==x))
    if remove and st.button('Delete selected document'):
      try: delete_vectors(store(f'{data_dir()}/chroma',make_embeddings(st.session_state.settings)),remove); delete_document(st.session_state.db,remove); st.rerun()
      except Exception as e: st.error(str(e))
