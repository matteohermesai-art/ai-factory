from pydantic import BaseModel
from typing import Optional, Dict, Any


class HermesArtifact(BaseModel):
    path: str
    content: str


class HermesNodeOutput(BaseModel):
    node_id: str
    agent: str
    type: str  # "python_module" | "sql" | "test" | "text"
    status: str  # SUCCESS | FAILED
    artifact: Optional[HermesArtifact] = None
    meta: Optional[Dict[str, Any]] = None
