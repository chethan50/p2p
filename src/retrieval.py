"""Filtered MMR retrieval and stable source labels."""
from __future__ import annotations
from langchain_core.documents import Document
def retrieve(vs, doc_ids:list[str], query:str, top_k:int=7)->list[Document]:
    if not doc_ids: return []
    # Chroma supports $in metadata filtering; one id is kept simple for compatibility.
    where={'doc_id':doc_ids[0]} if len(doc_ids)==1 else {'doc_id':{'$in':doc_ids}}
    return vs.max_marginal_relevance_search(query,k=top_k,fetch_k=max(20,top_k*3),filter=where)
def context_block(docs:list[Document])->tuple[str,dict[str,Document]]:
    mapping={f'S{i}':d for i,d in enumerate(docs,1)}
    text='\n\n'.join(f'[{sid}] {d.metadata["doc_name"]} — page {d.metadata["page"]}\n{d.page_content}' for sid,d in mapping.items())
    return text,mapping
