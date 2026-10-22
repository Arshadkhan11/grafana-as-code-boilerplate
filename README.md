# Grafana as Code — boilerplate

YAML config in. Dashboard JSON + alert JSON out. Validate before you apply.

This is a **public, fictional** starter — not a dump of any employer’s Grafana. It shows the same *operating model* used to run monitoring as a product: one template, many services, Git as source of truth.

## Why this exists

Click-ops Grafana does not survive 50+ microservices. You get:

- dashboards that only the original author understands
- alerts that page the wrong team
- no PR review, no rollback, no standard golden signals

This repo is the smallest honest version of the fix:

```
service.yaml  →  render  →  dashboards/*.json + alerts/*.json  →  validate  →  (your GitOps / Grafana API)
```

## Layout

```
grafana-as-code-boilerplate/
├── Makefile
├── scripts/render.py          # substitute {{placeholders}} from YAML
├── scripts/validate.py        # JSON + required PromQL fields
├── templates/
│   ├── dashboard.json.tmpl
│   └── alerts.json.tmpl
└── examples/payments-api/
    ├── service.yaml
    └── expected/              # golden files for make test
```

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make render SERVICE=examples/payments-api
make validate SERVICE=examples/payments-api
make test
```

Output lands in `examples/payments-api/generated/`.

## What a hiring manager should notice

- **Contract, not art.** `service.yaml` is the API developers fill in. Templates stay owned by platform.
- **Golden signals first.** Latency, traffic, errors, saturation — then optional Kafka / datastore rows.
- **Alerts are code.** Same labels as the dashboard; routing is a named contact point, not a screenshot.
- **CI-shaped.** `make test` diffs generated JSON against `expected/`. Wire that to GitHub Actions when your token has `workflow` scope.

## Not included (on purpose)

- Real datasource UIDs, folder UIDs, or production contact points
- Employer dashboard JSON
- A live Grafana apply step (that belongs behind a secret you do not commit)

Apply with your own token, or import JSON by hand in a throwaway Grafana.

## Config contract

See [`examples/payments-api/service.yaml`](examples/payments-api/service.yaml). Required keys:

| Key | Role |
| --- | --- |
| `microservice.name` | Folder / ownership |
| `microservice.service_name` | Must match Prometheus `service` label |
| `datasources.prometheus_uid` | Injected into every panel |
| `alerts.enabled` | If false, alerts file is an empty group |
| `monitoring.*` | Feature flags for optional rows |

## License

MIT. Fork it, rename the service, put it behind your Grafana.
