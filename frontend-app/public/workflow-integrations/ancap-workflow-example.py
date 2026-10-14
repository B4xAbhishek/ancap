"""Queue an explicitly budgeted ANCAP workflow and poll its status.

Set ANCAP_API_TOKEN, ANCAP_AUTOMATION_ID and ANCAP_MAX_COST_ACP.
The token is never printed. Use a token for a user who owns the automation.
"""
import json
import os
import time
from uuid import uuid4
from urllib.request import Request, urlopen
from urllib.parse import urlparse


def main():
    base = os.environ.get("ANCAP_API_URL", "https://api.ancap.cloud/v1").rstrip("/")
    parsed = urlparse(base)
    if parsed.scheme != "https" and parsed.hostname not in {"127.0.0.1", "localhost"}:
        raise SystemExit("Use HTTPS for remote endpoints")
    token = os.environ["ANCAP_API_TOKEN"]
    automation = os.environ["ANCAP_AUTOMATION_ID"]
    from uuid import UUID
    automation = str(UUID(automation))
    cap = os.environ["ANCAP_MAX_COST_ACP"]
    def call(path, body=None):
        request = Request(base+path, data=json.dumps(body).encode() if body is not None else None, headers={"Authorization": "Bearer "+token, "Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest"})
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    queued = call(f"/workflow-ops/automations/{automation}/runs", {"idempotency_key": str(uuid4()), "max_cost_acp": cap, "kind": "manual", "inputs": {}})
    run_id = queued["id"]
    print("Queued operation", run_id)
    for _ in range(180):
        result = call(f"/workflow-ops/runs/{run_id}")
        print(result["state"], "captured ACP:", result["cost_acp"])
        if result["state"] not in {"queued", "approved"}:
            # Awaiting review is intentionally terminal for this client: do not auto-approve.
            return
        time.sleep(5)
    raise SystemExit("Polling timeout; inspect the durable operation in Workflow Studio")


if __name__ == "__main__":
    main()
