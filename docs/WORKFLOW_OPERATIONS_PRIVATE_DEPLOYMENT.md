# Private Workflow Studio deployment

Workflow Studio is available at `/ai/studio`; integration instructions are at
`/docs/workflow-operations`. A downloaded private profile describes a deployment,
not a provisioned hosted tenant. Customer infrastructure and credentials are required.

1. Clone a reviewed release of https://github.com/ancapcloud/ancap and use
   `docker-compose.prod.yml` as the deployment baseline. Keep this database, ledger
   and keys separate from the public ANCAP installation.
2. Generate fresh values for `SECRET_KEY`, `POSTGRES_PASSWORD`, `CRON_SECRET` and
   `ACP_RPC_TOKEN`. Set platform administrator IDs, allowed origins, hostname/TLS,
   public frontend API URL and server API URL for this installation. Never reuse
   public production secrets or commit a populated environment file.
3. Choose the existing operator LLM configuration: tenant Anthropic/Teneta,
   customer Anthropic BYOK in Studio, or `LLM_PROVIDER=ollama` with
   `OLLAMA_BASE_URL` pointing to a customer-operated Ollama server and `LLM_MODEL`
   naming an installed model. Containers need a reachable internal hostname;
   `localhost` inside the API container is not the host machine.
4. Before starting application traffic, run `alembic upgrade head` against this
   installation's database. Migration `087_workflow_operations` creates the durable
   workspace, credential, version and operation tables.
5. Enable `WORKFLOW_OPERATIONS_WORKER_ENABLED=true` (the default). Check
   `/v1/system/ready` and `/v1/workflow-ops/capabilities`: worker `last_tick` should
   advance. The existing authenticated system job tick can also drain work.
6. Configure connector credentials locally. External delivery still needs outbound
   HTTPS access; an Ollama installation does not make connectors offline. Webhooks
   require public HTTPS and a signing secret; redirects/private-network addresses
   are refused. Google Sheets uses a customer OAuth access token, which must be
   replaced when it expires; automatic refresh/OAuth onboarding is not included.
7. Test on separate test credits: project → paid test → inspect quality/receipt →
   publish → capped run → review → approved delivery. Only authorize a destination
   you control. A saved credential is not proof of successful delivery.

The builder supports a bounded sequential plan of 1–5 steps, batches of 1–20 CSV
rows and schedules at least 60 minutes apart. It does not execute arbitrary code
or general branching graphs. ACP prices come from the existing live catalog;
BYOK does not waive ACP execution charges. There are no automatic deposits.

Back up the database and encryption root together: changing `SECRET_KEY` makes
existing connector envelopes unreadable. Plan credential rotation before replacing
it. Configure encrypted backups, restore drills, infrastructure monitoring and
perimeter access for the actual customer environment before calling it production.

Context retention starts at the last project update; each operation has its own
content-expiry deadline. Cleanup removes context and operation inputs/results while
keeping billing totals and receipt hashes. Saved workflow definitions and credentials
remain until their owner deletes them; database backups have a separate policy.

Delivery claims persist before network calls. An interrupted/uncertain delivery is
not automatically retried: first check the recipient, then explicitly retry in Studio.
Pausing a schedule prevents future enqueues; cancel an already queued operation
separately. Completed steps remain billable. Degraded model fallback refunds the
current reserved step and cannot be automatically delivered.
