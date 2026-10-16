import sqlite3
from src.ingestion import extract_upload
from src.vectorstore import page_chunks
from src.citations import parse_markers,verify_quote,resolve
from src.db import connect,add_document,documents,add_run,analytics
from src.schemas import EnhancedPromptResult,SummaryResult

def test_text_ingestion_and_page_metadata():
    doc=extract_upload('note.txt',b'hello world')
    assert doc.pages == ['hello world'] and doc.words == 2
    chunks=page_chunks('d','note.txt',['first page text','second page text'],20,0)
    assert {c.metadata['page'] for c in chunks} == {1,2}

def test_citations_and_quote_verification():
    assert parse_markers('Claim [S1], again [S1], [S2]') == ['1','2']
    assert verify_quote('revenue grew eighteen percent','Revenue grew 18 percent') is False

def test_sqlite_dedup_and_analytics(tmp_path):
    con=connect(tmp_path/'app.db'); row={'id':'one','name':'x','content_hash':'hash','pages':1,'words':2,'tokens':2}
    add_document(con,row); add_document(con,{**row,'id':'two'})
    assert len(documents(con)) == 1
    add_run(con,{'task':'Summarize','style':'Balanced','doc_ids':['one'],'original_prompt':'a','enhanced_prompt':'b','original_response':'{}','enhanced_response':'{}','judge_json':{'relevance':{'original':4,'enhanced':7,'justification':'better'}},'provider':'x','model':'y'})
    assert len(analytics(con)) == 1

def test_schema_contracts():
    assert EnhancedPromptResult(enhanced_prompt='x',retrieval_query='x').improvements == []
    assert SummaryResult(tldr='x',conclusion='y').key_points == []
