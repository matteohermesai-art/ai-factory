from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal


# -----------------------------
# INPUT MODELS (API → system)
# -----------------------------

class Requirement(BaseModel):
    title: str
    description: str


class Review(BaseModel):
    validation_status: Literal["PASS", "FAIL"]
    comments: str


class ArchitectureRequest(BaseModel):
    approach: str
    design_notes: str


class ADRRequest(BaseModel):
    req_id: int
    approach: str
    architecture: str
    tradeoffs: str


class ADRReview(BaseModel):
    status: Literal["PASS", "FAIL"]
    comments: str


class QARequest(BaseModel):
    test_command: str
    working_dir: str = "/tmp"


# -----------------------------
# HERMES OUTPUT SCHEMA
# -----------------------------

class HermesArtifact(BaseModel):
    path: str
    content: str


class HermesNodeOutput(BaseModel):
    node_id: str
    agent: str
    type: Literal["python_module", "sql", "test", "text"]
    status: Literal["SUCCESS", "FAILED"]

    artifact: Optional[HermesArtifact] = None
    meta: Optional[Dict[str, Any]] = None


# -----------------------------
# GRAPH STRUCTURES (optional future use)
# -----------------------------

class GraphNode(BaseModel):
    id: str
    agent: str
    input: str
    expected_output: Optional[str] = None


class GraphEdge(BaseModel):
    from_node: str
    to_node: str
