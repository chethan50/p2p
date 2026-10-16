import json, streamlit as st, altair as alt
from src.db import analytics
st.title('Enhancement analytics'); rows=analytics(st.session_state.db); data=[]
for r in rows:
  try:
    j=json.loads(r['judge_json'])
    for criterion,v in j.items():
      if isinstance(v,dict): data += [{'task':r['task'],'style':r['style'],'date':r['created_at'],'criterion':criterion,'version':'Original','score':v['original']},{'task':r['task'],'style':r['style'],'date':r['created_at'],'criterion':criterion,'version':'Enhanced','score':v['enhanced']}]
  except (ValueError,KeyError): pass
if not data: st.info('Run and judge a few comparisons to see score improvement analytics.');st.stop()
st.altair_chart(alt.Chart(alt.Data(values=data)).mark_bar().encode(x='criterion:N',y='mean(score):Q',color='version:N',column='style:N'),use_container_width=True)
st.dataframe(data,use_container_width=True)
