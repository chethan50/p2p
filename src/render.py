"""Shared Streamlit rendering helpers kept out of page business logic."""
from __future__ import annotations
import streamlit as st
from .citations import resolve
def citations(text,sources):
    items=resolve(text,sources)
    if items:
        st.caption('Sources')
        for x in items:
            st.markdown(f"`{'✓' if x['valid'] else '⚠'} {x['doc_name']} - p.{x['page'] or '?'}`")
            if x['valid']:
                with st.expander(f"[ {x['id']} ] source passage"): st.write(x['passage'])
def result_card(obj):
    data=obj.model_dump() if hasattr(obj,'model_dump') else obj
    for key,value in data.items():
        if isinstance(value,list):
            with st.expander(key.replace('_',' ').title(),expanded=True): st.write(value)
        else: st.markdown(f'**{key.replace("_"," ").title()}**  \n{value}')
