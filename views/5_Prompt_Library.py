import json, streamlit as st
from src.db import runs,templates,add_template,toggle_favorite
st.title('Prompt library')
query=st.text_input('Search history'); rows=runs(st.session_state.db); rows=[r for r in rows if query.lower() in (r['original_prompt']+r['enhanced_prompt']).lower()]
for r in rows:
  with st.expander(f"#{r['id']} · {r['task']} · {r['style']} · {r['created_at']}"):
    st.write(r['enhanced_prompt']); c1,c2,c3=st.columns(3)
    if c1.button('Reuse',key=f'reuse{r["id"]}'): st.session_state.reuse_prompt=r['enhanced_prompt'];st.switch_page('views/2_Ask.py')
    if c2.button('★' if not r['favorite'] else 'Unstar',key=f'star{r["id"]}'): toggle_favorite(st.session_state.db,r['id'],not r['favorite']);st.rerun()
    if c3.button('Save template',key=f'tpl{r["id"]}'): add_template(st.session_state.db,f"Run {r['id']}",r['enhanced_prompt']);st.success('Template saved')
st.subheader('Reusable templates')
for t in templates(st.session_state.db): st.write(f"**{t['name']}** — {t['tags']}")
st.download_button('Export library JSON',json.dumps(rows,indent=2),file_name='prompt-library.json')
