"""LCEL structured chains, including blind randomized judging."""
from __future__ import annotations
import random
from concurrent.futures import ThreadPoolExecutor
from typing import Type
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from . import prompts
from .schemas import *
TASK_MODELS:dict[str,Type]={'Summarize':SummaryResult,'Extract Insights':InsightsResult,'Identify Trends':TrendsResult,'Generate Recommendations':RecommendationsResult,'Custom':CustomResult}
DEFAULTS={'Summarize':'Summarize the most important points.','Extract Insights':'Extract important insights and their evidence.','Identify Trends':'Identify trends, anomalies and supporting evidence.','Generate Recommendations':'Generate document-grounded recommendations.','Custom':'Answer the question using the documents.'}
def structured(llm, template:str, model:Type, **values):
    prompt=ChatPromptTemplate.from_template(template)
    try:
        result=(prompt | llm.with_structured_output(model)).invoke(values)
        if result is None:
            raise ValueError('The provider returned an empty structured response.')
        return result if isinstance(result,model) else model.model_validate(result)
    except Exception:
        parser=PydanticOutputParser(pydantic_object=model)
        fallback=ChatPromptTemplate.from_template(template+'\nReturn only JSON matching:\n{format_instructions}')
        chain=fallback.partial(format_instructions=parser.get_format_instructions()) | llm | parser
        # A malformed provider response is retried once before surfacing a readable page error.
        try:
            return chain.invoke(values)
        except Exception:
            return chain.invoke(values)
def enhance(llm, question:str, task:str, style:str, preview:str)->EnhancedPromptResult:
    return structured(llm,prompts.ENHANCER,EnhancedPromptResult,question=question or DEFAULTS[task],task=task,style=style,preview=preview)
def answer(llm, task:str, prompt:str, context:str): return structured(llm,prompts.ANSWER,TASK_MODELS[task],prompt=prompt,context=context)
def compare_answers(llm,task:str,original:str,enhanced:str,context:str):
    with ThreadPoolExecutor(max_workers=2) as pool:
        a=pool.submit(answer,llm,task,original,context); b=pool.submit(answer,llm,task,enhanced,context)
        return a.result(),b.result()
def judge(llm,intent:str,context:str,original:str,enhanced:str,rng=random):
    flipped=bool(rng.choice([False,True])); a,b=(enhanced,original) if flipped else (original,enhanced)
    raw=structured(llm,prompts.JUDGE,JudgeResult,intent=intent,context=context,a=a,b=b)
    # Models return A/B in schema's winner field only when coerced externally; normalize it.
    winner=raw.winner
    if flipped:
        for c in ('relevance','completeness','structure','actionability','groundedness'):
            x=getattr(raw,c); x.original,x.enhanced=x.enhanced,x.original
        winner={'original':'enhanced','enhanced':'original','A':'enhanced','B':'original'}.get(winner,winner)
    return raw.model_copy(update={'winner':{'A':'original','B':'enhanced'}.get(winner,winner)})
def conflicts(llm, topic:str, claims:str)->ConflictReport: return structured(llm,prompts.CONFLICT,ConflictReport,topic=topic or 'all salient topics',claims=claims)
