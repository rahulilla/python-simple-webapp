# multi-agent-demo-app

A tiny Flask web app with a `/health` endpoint. This repo is the **target**
for the multi-agent code review system: open a PR here, the reviewer (running
out of [`MultiAgentCodeReview`](https://github.com/rahulilla/MultiAgentCodeReview))
analyses the change and suggests fixes; the GitHub Actions workflow in this
repo verifies the app still boots and `/health` returns `200` after the merge.

## Endpoints

| Method | Path      | Response                                                |
|--------|-----------|---------------------------------------------------------|
| GET    | `/`       | text banner — `multi-agent-demo-app v0.1.0`             |
| GET    | `/health` | JSON — `{"status":"ok","version":"...","uptime_seconds":N}` |

## Run locally

```bash
pip install -r requirements.txt
python app.py
# in another shell:
curl -s http://127.0.0.1:8000/health
```

## Run the tests

```bash
pip install -r requirements.txt
pytest -q tests
```

## CI

`.github/workflows/health-check.yml` runs on every push to `main` and every PR:

1. Install deps
2. Run `pytest`
3. Boot the app in the background, wait for the port
4. `curl /health` — assert HTTP 200 + `status: ok`

If the app fails to come up the workflow uploads `webapp.log` as an artifact.

## Layout

```
.
├── app.py                            # Flask app + create_app() factory
├── requirements.txt                  # flask, pytest
├── tests/
│   ├── conftest.py                   # makes the repo root importable
│   └── test_app.py                   # endpoint + payload-shape tests
└── .github/
    └── workflows/
        └── health-check.yml          # test + live /health probe
```
