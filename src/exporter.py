"""Run export helpers."""
from __future__ import annotations
import json
def as_json(value:dict)->str: return json.dumps(value,indent=2,default=str)
def as_markdown(run:dict)->str:
    return f"# Prompt Lab run\n\n## Original prompt\n{run.get('original_prompt','')}\n\n## Enhanced prompt\n{run.get('enhanced_prompt','')}\n\n## Original answer\n{run.get('original_response','')}\n\n## Enhanced answer\n{run.get('enhanced_response','')}"
