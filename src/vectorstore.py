"""Chroma persistence with page-isolated chunking."""
from __future__ import annotations
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
def page_chunks(doc_id:str,name:str,pages:list[str],size:int=1000,overlap:int=150)->list[Document]:
    splitter=RecursiveCharacterTextSplitter(chunk_size=size,chunk_overlap=overlap); result=[]
    for page_no,text in enumerate(pages,1):
        for i,chunk in enumerate(splitter.split_text(text)):
            result.append(Document(page_content=chunk,metadata={'doc_id':doc_id,'doc_name':name,'page':page_no,'chunk_index':i}))
    return result
def store(directory:str,embeddings): return Chroma(collection_name='prompt_lab',persist_directory=directory,embedding_function=embeddings)
def add_documents(vs,docs:list[Document],doc_id:str)->None: vs.add_documents(docs,ids=[f'{doc_id}:{d.metadata["page"]}:{d.metadata["chunk_index"]}' for d in docs])
def delete_document(vs,doc_id:str)->None: vs.delete(where={'doc_id':doc_id})
