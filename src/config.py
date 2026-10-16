"""Provider factories and settings; no key is persisted."""
from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()
@dataclass
class Settings:
    provider:str='Gemini'; model:str='gemini-3.5-flash-lite'; embeddings:str='Gemini'; temperature:float=.2; api_key:str=''; top_k:int=7; chunk_size:int=1000
def data_dir()->str: return os.getenv('PROMPT_LAB_DATA_DIR','data')
def make_llm(s:Settings):
    key=s.api_key or os.getenv({'Gemini':'GOOGLE_API_KEY','OpenAI':'OPENAI_API_KEY','Anthropic':'ANTHROPIC_API_KEY'}[s.provider],'')
    if not key: raise ValueError(f'Missing API key for {s.provider}. Add it in the sidebar or .env.')
    if s.provider=='Gemini':
        from langchain_google_genai import ChatGoogleGenerativeAI
        # Keep UI failures prompt: provider defaults can otherwise retry for minutes.
        return ChatGoogleGenerativeAI(model=s.model,google_api_key=key,temperature=s.temperature,max_retries=1,timeout=30)
    if s.provider=='OpenAI':
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=s.model,api_key=key,temperature=s.temperature)
    from langchain_anthropic import ChatAnthropic
    return ChatAnthropic(model=s.model,api_key=key,temperature=s.temperature)
def make_embeddings(s:Settings):
    env_name='GOOGLE_API_KEY' if s.embeddings=='Gemini' else 'OPENAI_API_KEY'
    # GEMINI_API_KEY is accepted too, which is convenient for Gemini's own docs.
    key=s.api_key or os.getenv(env_name,'') or (os.getenv('GEMINI_API_KEY','') if s.embeddings=='Gemini' else '')
    if s.embeddings != 'HuggingFace' and not key:
        raise ValueError(f'Missing API key for {s.embeddings} embeddings. Add {env_name} to .env or enter a key in the sidebar.')
    if s.embeddings=='Gemini':
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        # text-embedding-004 is retired on Gemini's v1beta embedContent API.
        return GoogleGenerativeAIEmbeddings(model='models/gemini-embedding-001',google_api_key=key)
    if s.embeddings=='OpenAI':
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model='text-embedding-3-small',api_key=key)
    from langchain_community.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
