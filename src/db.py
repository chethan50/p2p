"""SQLite registry and history persistence."""
from __future__ import annotations
import json, sqlite3
from pathlib import Path
from typing import Any
SCHEMA = '''
CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, name TEXT, content_hash TEXT UNIQUE, pages INTEGER, words INTEGER, tokens INTEGER, status TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS runs (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, task TEXT, style TEXT, doc_ids TEXT, original_prompt TEXT, enhanced_prompt TEXT, original_response TEXT, enhanced_response TEXT, judge_json TEXT, provider TEXT, model TEXT, favorite INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS templates (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, prompt TEXT, tags TEXT, notes TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS chats (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, summary TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, role TEXT, content TEXT, enhanced_prompt TEXT, citations TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
'''
def connect(path: str | Path) -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True); con=sqlite3.connect(path, check_same_thread=False); con.row_factory=sqlite3.Row; con.executescript(SCHEMA); con.commit(); return con
def add_document(con: sqlite3.Connection, row: dict[str, Any]) -> None:
    con.execute('INSERT OR IGNORE INTO documents(id,name,content_hash,pages,words,tokens,status) VALUES(?,?,?,?,?,?,?)',(row['id'],row['name'],row['content_hash'],row['pages'],row['words'],row['tokens'],row.get('status','ready'))); con.commit()
def documents(con: sqlite3.Connection) -> list[dict[str,Any]]: return [dict(r) for r in con.execute('SELECT * FROM documents ORDER BY created_at DESC')]
def delete_document(con: sqlite3.Connection, doc_id: str) -> None: con.execute('DELETE FROM documents WHERE id=?',(doc_id,)); con.commit()
def add_run(con: sqlite3.Connection, run: dict[str,Any]) -> int:
    keys=['task','style','doc_ids','original_prompt','enhanced_prompt','original_response','enhanced_response','judge_json','provider','model']; vals=[json.dumps(run[k]) if k in ('doc_ids','judge_json') else run.get(k,'') for k in keys]; cur=con.execute(f'INSERT INTO runs({",".join(keys)}) VALUES({",".join("?"*len(keys))})',vals); con.commit(); return int(cur.lastrowid)
def runs(con: sqlite3.Connection) -> list[dict[str,Any]]: return [dict(r) for r in con.execute('SELECT * FROM runs ORDER BY id DESC')]
def toggle_favorite(con: sqlite3.Connection, run_id:int, value:bool)->None: con.execute('UPDATE runs SET favorite=? WHERE id=?',(int(value),run_id));con.commit()
def add_template(con:sqlite3.Connection,name:str,prompt:str,tags:str='',notes:str='')->None: con.execute('INSERT INTO templates(name,prompt,tags,notes) VALUES(?,?,?,?)',(name,prompt,tags,notes));con.commit()
def templates(con:sqlite3.Connection)->list[dict[str,Any]]: return [dict(r) for r in con.execute('SELECT * FROM templates ORDER BY id DESC')]
def add_chat(con:sqlite3.Connection,title:str)->int: cur=con.execute('INSERT INTO chats(title) VALUES(?)',(title,));con.commit();return int(cur.lastrowid)
def chats(con:sqlite3.Connection)->list[dict[str,Any]]: return [dict(r) for r in con.execute('SELECT * FROM chats ORDER BY id DESC')]
def messages(con:sqlite3.Connection,chat_id:int)->list[dict[str,Any]]: return [dict(r) for r in con.execute('SELECT * FROM messages WHERE chat_id=? ORDER BY id',(chat_id,))]
def add_message(con:sqlite3.Connection,chat_id:int,role:str,content:str,enhanced:str='',citations:str='')->None: con.execute('INSERT INTO messages(chat_id,role,content,enhanced_prompt,citations) VALUES(?,?,?,?,?)',(chat_id,role,content,enhanced,citations));con.commit()
def analytics(con:sqlite3.Connection)->list[dict[str,Any]]:
    return [dict(r) for r in con.execute("SELECT task,style,created_at,judge_json FROM runs WHERE judge_json != ''")]
