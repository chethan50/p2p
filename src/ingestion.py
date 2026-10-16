"""Safe per-page document extraction."""
from __future__ import annotations
from dataclasses import dataclass
from io import BytesIO
from pypdf import PdfReader
from .utils import content_hash,estimate_tokens
@dataclass
class ExtractedDocument:
    name:str; content_hash:str; pages:list[str]; words:int; tokens:int
def extract_upload(name:str,data:bytes)->ExtractedDocument:
    suffix=name.lower().rsplit('.',1)[-1]; pages:list[str]=[]
    if suffix=='pdf':
        reader=PdfReader(BytesIO(data))
        if reader.is_encrypted: raise ValueError('This PDF is encrypted and cannot be read.')
        pages=[p.extract_text() or '' for p in reader.pages]
        if not any(p.strip() for p in pages): raise ValueError('No extractable text found (possibly scanned). OCR is not supported.')
    elif suffix in ('txt','md'): pages=[data.decode('utf-8',errors='replace')]
    else: raise ValueError('Supported formats are PDF, TXT and Markdown.')
    text='\n'.join(pages); return ExtractedDocument(name,content_hash(data),pages,len(text.split()),estimate_tokens(text))
