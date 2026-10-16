"""Typed contracts returned by Prompt Lab chains."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

class Citation(BaseModel):
    source_id: str

class SummaryResult(BaseModel):
    tldr: str
    key_points: list[str] = Field(default_factory=list)
    important_entities: list[str] = Field(default_factory=list)
    conclusion: str

class Insight(BaseModel):
    title: str; explanation: str; evidence_quote: str = ""; importance: Literal['high','medium','low'] = 'medium'; citations: list[str] = Field(default_factory=list)
class InsightsResult(BaseModel): insights: list[Insight] = Field(default_factory=list)
class Trend(BaseModel):
    name: str; direction: Literal['rising','falling','stable','emerging'] = 'stable'; evidence: str; confidence: str = 'medium'; citations: list[str] = Field(default_factory=list)
class TrendsResult(BaseModel): trends: list[Trend] = Field(default_factory=list); anomalies: list[str] = Field(default_factory=list)
class Recommendation(BaseModel):
    action: str; rationale: str; priority: str = 'medium'; effort: str = 'medium'; expected_impact: str = ''; citations: list[str] = Field(default_factory=list)
class RecommendationsResult(BaseModel): recommendations: list[Recommendation] = Field(default_factory=list); risks: list[str] = Field(default_factory=list)
class CustomResult(BaseModel): answer: str; key_takeaways: list[str] = Field(default_factory=list); citations: list[str] = Field(default_factory=list)
class Improvement(BaseModel): what: str; why: str
class EnhancedPromptResult(BaseModel): enhanced_prompt: str; retrieval_query: str; improvements: list[Improvement] = Field(default_factory=list)
class CriterionScore(BaseModel): original: int = Field(ge=1,le=10); enhanced: int = Field(ge=1,le=10); justification: str
class JudgeResult(BaseModel):
    relevance: CriterionScore; completeness: CriterionScore; structure: CriterionScore; actionability: CriterionScore; groundedness: CriterionScore
    winner: Literal['original','enhanced','tie']; summary: str
class Claim(BaseModel): claim: str; citations: list[str] = Field(default_factory=list)
class DocumentClaims(BaseModel): document_id: str; claims: list[Claim] = Field(default_factory=list)
class Position(BaseModel): document_id: str; position: str; citations: list[str] = Field(default_factory=list)
class ConflictTopic(BaseModel): topic: str; status: Literal['agree','conflict','partial','unique']; positions: list[Position] = Field(default_factory=list); explanation: str; severity: Literal['high','medium','low'] = 'low'
class ConflictReport(BaseModel): topics: list[ConflictTopic] = Field(default_factory=list)
