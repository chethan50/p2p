"""Prompt Lab for Documents entry point: navigation and sidebar only."""
from __future__ import annotations
import streamlit as st
from src.config import Settings, data_dir
from src.db import connect, documents
st.set_page_config(page_title='Prompt Lab for Documents',page_icon='🔬',layout='wide')
if 'settings' not in st.session_state: st.session_state.settings=Settings()
if 'db' not in st.session_state: st.session_state.db=connect(f'{data_dir()}/app.db')
s=st.session_state.settings
with st.sidebar:
    st.header('Prompt Lab')
    s.provider=st.selectbox('LLM provider',['Gemini','OpenAI','Anthropic'],index=['Gemini','OpenAI','Anthropic'].index(s.provider))
    defaults={'Gemini':'gemini-3.5-flash-lite','OpenAI':'gpt-4o-mini','Anthropic':'claude-3-5-haiku-latest'}
    # Migrate sessions created before Gemini 2.0 Flash was shut down.
    if s.provider=='Gemini' and s.model=='gemini-2.0-flash': s.model=defaults['Gemini']
    s.model=st.text_input('Model',s.model or defaults[s.provider])
    s.embeddings=st.selectbox('Embeddings',['Gemini','OpenAI','HuggingFace'],index=['Gemini','OpenAI','HuggingFace'].index(s.embeddings))
    s.temperature=st.slider('Temperature',0.0,1.0,s.temperature,.05)
    s.api_key=st.text_input('API key override',type='password',help='Stored only for this browser session.')
    s.top_k=st.slider('Sources to retrieve',3,12,s.top_k)
    s.chunk_size=st.slider('Chunk size',400,1800,s.chunk_size,100)
    st.session_state.enable_judge=st.toggle('Enable judge',value=st.session_state.get('enable_judge',True))
    st.caption(f"{len(documents(st.session_state.db))} documents in workspace")
pages=[
    st.Page('views/1_Workspace.py', title='Workspace', icon='📄'),
    st.Page('views/2_Ask.py', title='Ask', icon='✨'),
    st.Page('views/3_Chat.py', title='Chat', icon='💬'),
    st.Page('views/4_Compare_Documents.py', title='Compare Documents', icon='⚖️'),
    st.Page('views/5_Prompt_Library.py', title='Prompt Library', icon='📚'),
    st.Page('views/6_Analytics.py', title='Analytics', icon='📈'),
]
st.navigation(pages).run()
