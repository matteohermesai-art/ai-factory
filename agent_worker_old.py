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
# Hermes runner (FIXED)
# -------------------------
def run_hermes(prompt):
    try:
        result = subprocess.run(
            ["hermes", "run", prompt],
            capture_output=True,
            text=True
        )
        return result
    except Exception as e:
        class R:
            returncode = -1
            stdout = ""
            stderr = str(e)
        return R()


# -------------------------
# Parse output (SAFE)
# -------------------------
def parse_hermes_output(raw):
    try:
        data = json.loads(raw)
        return data
    except Exception:
        return None


# -------------------------
# Artifact writer
# -------------------------
def write_artifact(node_id, content):
    node_dir = os.path.join(ARTIFACT_ROOT, f"node_{node_id}")
    os.makedirs(node_dir, exist_ok=True)

    path = os.path.join(node_dir, "output.txt")

    with open(path, "w") as f:
        f.write(content or "")

    return path


# -------------------------
# Fetch events
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
# Graph builder (stub)
# -------------------------
def build_graph(payload):
    prompt = f"""
You are an autonomous system designer.

Generate a full execution DAG for this requirement:

{payload}

Rules:
- Do NOT limit number of nodes
- Decompose until tasks are atomic
- Assign agents automatically (architect, developer, qa, worker)
- Define dependencies
- Output JSON only:
  nodes: id, agent, input, expected_output
  edges: from, to
"""
    result = run_hermes(prompt)
    return result.stdout.strip()


# -------------------------
# PROCESS EVENT
# -------------------------
def process_event(event):
    event_id, entity_type, entity_id, event_type, payload = event

    print(f"[GRAPH MODE] {event_type}")

    graph_json = build_graph(payload)

    try:
        graph = json.loads(graph_json)
    except Exception:
        print("[ERROR] invalid graph JSON")
        return


    nodes = {n["id"]: n for n in graph["nodes"]}
    deps = {n["id"]: [] for n in graph["nodes"]}

    for e in graph["edges"]:
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

            result = run_hermes(node["input"])
            output = (result.stdout or "").strip()

            artifact = write_artifact(node_id, output)

            success = result.returncode == 0 and output != ""

            outputs[node_id] = {
                "output": output,
                "artifact": artifact
            }

            state[node_id] = "SUCCESS" if success else "FAILED"
            changed = True

            # -------------------------
            # SIMPLE RETRY (1x)
            # -------------------------
            if state[node_id] == "FAILED":
                print(f"[RETRY] node {node_id}")

                retry = run_hermes(node["input"])
                retry_output = (retry.stdout or "").strip()

                retry_success = retry.returncode == 0 and retry_output != ""

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
