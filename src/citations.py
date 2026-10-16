"""Citation marker parsing and conservative quote validation."""
from __future__ import annotations
import re
from difflib import SequenceMatcher
from langchain_core.documents import Document
def parse_markers(text:str)->list[str]: return list(dict.fromkeys(re.findall(r'\[S(\d+)\]',text)))
def resolve(text:str, sources:dict[str,Document], quote:str='')->list[dict]:
    out=[]
    for n in parse_markers(text):
        key=f'S{n}'; d=sources.get(key)
        out.append({'id':key,'valid':d is not None,'doc_name':d.metadata['doc_name'] if d else 'Unknown','page':d.metadata['page'] if d else None,'passage':d.page_content if d else '', 'verified':verify_quote(quote,d.page_content) if d and quote else None})
    return out
def verify_quote(quote:str, passage:str, threshold:float=.72)->bool:
    q=' '.join(re.sub(r'[^\w\s]','',quote.lower()).split()); p=' '.join(re.sub(r'[^\w\s]','',passage.lower()).split())
    return bool(q) and (q in p or SequenceMatcher(None,q,p).ratio()>=threshold)
