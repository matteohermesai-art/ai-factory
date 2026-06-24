import psycopg2
import time
import subprocess
import os
import json

ARTIFACT_ROOT = "/home/orin/ai-factory/workspace/artifacts"

DB_CONFIG = {
    "dbname": "aifactory",
    "user": "aifactory",
    "password": "aifactory",
    "host": "localhost",
    "port": 5432
}

# -------------------------
# DB
# -------------------------
def get_conn():
    return psycopg2.connect(**DB_CONFIG)


# -------------------------
# HERMES RUNNER (STREAM SAFE + TRUNCATION SAFE)
# -------------------------
def run_hermes(prompt):
    result = subprocess.run(
        ["hermes", "run", prompt],
        capture_output=True,
        text=True
    )

    raw = result.stdout or ""

    # 1. Try JSONL streaming format
    chunks = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                # standard hermes streaming fields
                if "response" in obj:
                    chunks.append(obj["response"])
                elif "content" in obj:
                    chunks.append(obj["content"])
        except:
            continue

    output = "".join(chunks).strip()

    # 2. fallback: if not stream JSON, just raw stdout
    if not output:
        output = raw.strip()

    return output, result.returncode, raw


# -------------------------
# ARTIFACT WRITER
# -------------------------
def write_artifact(node_id, content):
    node_dir = os.path.join(ARTIFACT_ROOT, f"node_{node_id}")
    os.makedirs(node_dir, exist_ok=True)

    path = os.path.join(node_dir, "output.txt")

    with open(path, "w") as f:
        f.write(content or "")

    return path


# -------------------------
# FETCH EVENTS
# -------------------------
def fetch_events():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT event_id, entity_type, entity_id, event_type, payload
        FROM events
        WHERE status = 'PENDING'
        ORDER BY created_at ASC
        LIMIT 5
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# -------------------------
# GRAPH BUILDER
# -------------------------
def build_graph(payload):
    prompt = f"""
You are a deterministic orchestration engine.

Convert this requirement into a DAG.

Return ONLY JSON:

{{
  "nodes": [
    {{"id": "1", "agent": "architect", "input": "..."}}
  ],
  "edges": [
    {{"from": "1", "to": "2"}}
  ]
}}

Requirement:
{payload}
"""

    output, _, _ = run_hermes(prompt)
    return output


# -------------------------
# SAFE JSON PARSER
# -------------------------
def safe_parse_json(text):
    if not text:
        return None

    try:
        return json.loads(text)
    except:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except:
                return None
        return None


# -------------------------
# PROCESS EVENT (DAG EXECUTION ENGINE)
# -------------------------
def process_event(event):
    event_id, entity_type, entity_id, event_type, payload = event

    print(f"[GRAPH MODE] {event_type}")

    graph_json = build_graph(payload)
    graph = safe_parse_json(graph_json)

    if not graph:
        print("[ERROR] invalid graph JSON")
        print(graph_json[:500])
        return

    nodes = {n["id"]: n for n in graph["nodes"]}
    deps = {n["id"]: [] for n in graph["nodes"]}

    for e in graph.get("edges", []):
        deps[e["to"]].append(e["from"])

    state = {n: "PENDING" for n in nodes}
    outputs = {}

    changed = True

    while changed:
        changed = False

        for node_id, node in nodes.items():

            if state[node_id] == "SUCCESS":
                continue

            if any(state[d] != "SUCCESS" for d in deps[node_id]):
                continue

            print(f"[EXEC] node {node_id} via {node['agent']}")

            output, code, raw = run_hermes(node["input"])

            artifact = write_artifact(node_id, output)

            # -------------------------
            # STABILITY FIX (IMPORTANT)
            # -------------------------
            is_truncated = (
                "finish_reason='length'" in raw or
                "truncated" in raw.lower() or
                "Response remained truncated" in raw
            )
            
            if is_truncated:
                print(f"[WARN] node {node_id} output truncated")

            success = (
                code == 0 and
                len(output) > 0
            )

            state[node_id] = "SUCCESS" if success else "FAILED"
            changed = True

            # -------------------------
            # SINGLE RETRY ONLY
            # -------------------------
            if not success:
                print(f"[RETRY] node {node_id}")

                retry_output, retry_code, retry_raw = run_hermes(node["input"])

                retry_is_truncated = (
                    "finish_reason='length'" in retry_raw or
                    "truncated" in retry_raw.lower()
                )

                retry_success = (
                    retry_code == 0 and
                    len(retry_output) > 0 and
                    not retry_is_truncated
                )

                if retry_success:
                    state[node_id] = "SUCCESS"
                    outputs[node_id]["output"] = retry_output
                    write_artifact(node_id + "_retry", retry_output)


# -------------------------
# LOOP
# -------------------------
def loop():
    while True:
        events = fetch_events()

        for e in events:
            process_event(e)

        time.sleep(2)


if __name__ == "__main__":
    loop()
