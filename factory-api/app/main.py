from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import subprocess
import os
from app.schemas import HermesNodeOutput

app = FastAPI()

DB_CONFIG = {
    "dbname": "aifactory",
    "user": "aifactory",
    "password": "aifactory",
    "host": "localhost",
    "port": 5432
}

VALID_STATES = [
    "DRAFT",
    "IN_REVIEW",
    "CHANGES_REQUESTED",
    "APPROVED",
    "ARCHITECTURE",
    "ADR_DRAFT",
    "ADR_REVIEW",
    "ADR_APPROVED",
    "DEV_DRAFT",
    "DEV_IN_PROGRESS",
    "DEV_REVIEW",
    "DEV_APPROVED",
    "QA_PENDING",
    "QA_RUNNING",
    "QA_FAILED",
    "QA_PASSED"
]

class Requirement(BaseModel):
    title: str
    description: str

class Review(BaseModel):
    validation_status: str
    comments: str

def get_conn():
    return psycopg2.connect(**DB_CONFIG)
    
def parse_hermes_output(raw: str):
    try:
        data = json.loads(raw)
        return HermesNodeOutput(**data)
    except Exception as e:
        print(f"[PARSE ERROR] {e}")
        return None

# -------------------------
# REQUIREMENTS
# -------------------------
@app.post("/requirements")
def create_requirement(req: Requirement):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO requirements (title, description, status, validation_status, version)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING req_id;
    """, (req.title, req.description, "DRAFT", "PENDING", 1))

    req_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return {"req_id": req_id, "status": "DRAFT"}

# -------------------------
# REQUIREMENT REVIEW
# -------------------------
@app.post("/requirements/{req_id}/review")
def review_requirement(req_id: int, review: Review):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE requirements
        SET validation_status = %s
        WHERE req_id = %s
    """, (review.validation_status, req_id))

    if review.validation_status == "FAIL":
        new_status = "CHANGES_REQUESTED"
    elif review.validation_status == "PASS":
        new_status = "APPROVED"
    else:
        new_status = "IN_REVIEW"

    if review.validation_status in ["FAIL", "CHANGES_REQUESTED"]:
        cur.execute("""
            UPDATE requirements
            SET status = %s,
                version = version + 1
            WHERE req_id = %s
        """, ("CHANGES_REQUESTED", req_id))
    else:
        cur.execute("""
            UPDATE requirements
            SET status = %s
            WHERE req_id = %s
        """, (new_status, req_id))

    conn.commit()
    cur.close()
    conn.close()

    return {
        "req_id": req_id,
        "status": new_status,
        "validation": review.validation_status
    }

# -------------------------
# ARCHITECTURE PROMOTION
# -------------------------
@app.post("/requirements/{req_id}/promote-to-architecture")
def promote_to_architecture(req_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE requirements
        SET status = %s
        WHERE req_id = %s
    """, ("ARCHITECTURE", req_id))

    conn.commit()
    cur.close()
    conn.close()

    return {"req_id": req_id, "status": "ARCHITECTURE"}

# -------------------------
# ADR CREATE
# -------------------------
class ADRRequest(BaseModel):
    req_id: int
    approach: str
    architecture: str
    tradeoffs: str

@app.post("/adr/create")
def create_adr(adr: ADRRequest):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO adr (title, decision, rationale)
        VALUES (%s, %s, %s)
        RETURNING adr_id;
    """, (
        f"ADR for REQ {adr.req_id}",
        adr.architecture,
        adr.tradeoffs
    ))

    adr_id = cur.fetchone()[0]

    cur.execute("""
        UPDATE requirements
        SET status = %s
        WHERE req_id = %s
    """, ("ADR_DRAFT", adr.req_id))

    conn.commit()
    cur.close()
    conn.close()

    return {
        "adr_id": adr_id,
        "req_id": adr.req_id,
        "status": "ADR_DRAFT"
    }

# -------------------------
# ADR REVIEW
# -------------------------
class ADRReview(BaseModel):
    status: str
    comments: str

@app.post("/adr/{adr_id}/review")
def review_adr(adr_id: int, review: ADRReview):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE adr
        SET rationale = rationale || %s
        WHERE adr_id = %s
    """, (f"\nREVIEW: {review.comments}", adr_id))

    new_status = "ADR_APPROVED" if review.status == "PASS" else "ADR_REVIEW"

    cur.execute("""
        UPDATE requirements
        SET status = %s
        WHERE req_id = (
            SELECT req_id FROM adr WHERE adr_id = %s
        )
    """, (new_status, adr_id))

    conn.commit()
    cur.close()
    conn.close()

    return {"adr_id": adr_id, "status": new_status}

# -------------------------
# DEV PROMOTION
# -------------------------
@app.post("/adr/{adr_id}/promote-to-dev")
def promote_to_dev(adr_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE requirements
        SET status = %s
        WHERE req_id = (
            SELECT req_id FROM adr WHERE adr_id = %s
        )
    """, ("DEV_DRAFT", adr_id))

    conn.commit()
    cur.close()
    conn.close()

    return {"adr_id": adr_id, "status": "DEV_DRAFT"}

# -------------------------
# QA (FIXED BUT MINIMAL)
# -------------------------
class QARequest(BaseModel):
    test_command: str
    working_dir: str = "/tmp"

@app.post("/adr/{adr_id}/validate")
def run_qa(adr_id: int, qa: QARequest):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE requirements
        SET status = %s
        WHERE req_id = (
            SELECT req_id FROM adr WHERE adr_id = %s
        )
    """, ("QA_RUNNING", adr_id))

    conn.commit()

    cwd = qa.working_dir if qa.working_dir and os.path.exists(qa.working_dir) else "/tmp"

    result = subprocess.run(
        qa.test_command,
        shell=True,
        capture_output=True,
        text=True,
        cwd=cwd
    )

    success = result.returncode == 0
    final_status = "QA_PASSED" if success else "QA_FAILED"

    cur.execute("""
        UPDATE requirements
        SET status = %s
        WHERE req_id = (
            SELECT req_id FROM adr WHERE adr_id = %s
        )
    """, (final_status, adr_id))

    conn.commit()
    cur.close()
    conn.close()

    return {
        "adr_id": adr_id,
        "status": final_status,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode
    }
    
@app.post("/events")
def create_event(event: dict):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO events (entity_type, entity_id, event_type, payload)
        VALUES (%s, %s, %s, %s)
        RETURNING event_id;
    """, (
        event["entity_type"],
        event["entity_id"],
        event["event_type"],
        psycopg2.extras.Json(event.get("payload", {}))
    ))

    event_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return {"event_id": event_id, "status": "PENDING"}
    
@app.post("/adr/{adr_id}/trigger-qa")
def trigger_qa(adr_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO events (entity_type, entity_id, event_type, payload)
        VALUES ('ADR', %s, 'RUN_QA', %s)
    """, (
        adr_id,
        psycopg2.extras.Json({
            "test_command": "echo test",
            "cwd": "/tmp"
        })
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "QUEUED"}
