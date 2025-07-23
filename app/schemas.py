from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., example="46-year-old male knee surgery Pune 3-month policy")

class Clause(BaseModel):
    text: str
    source: str

class DecisionResponse(BaseModel):
    decision: str  # approved / rejected / partial
    amount: float | None
    justification: str
    clauses: list[Clause]
