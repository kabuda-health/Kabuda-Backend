dev:
	uv run -m app.main

format:
	uv run -- ruff check --select I --fix
	uv run -- ruff format
	uv run -- taplo fmt

lint:
	uv run -- pyright app
	uv run -- mypy app
	uv run -- ruff check
	uv run -- ruff format --check

test:
	uv run -- pytest -v

migrate:
	uv run -- alembic upgrade head

TAG ?= $(shell git rev-parse --short HEAD)

GCLOUD_PROJECT_ID=careful-granite-450104-s7

IMAGE_NAME = us-west2-docker.pkg.dev/$(GCLOUD_PROJECT_ID)/kabuda-backend/api-server

deploy:
	gcloud builds submit --substitutions=_IMAGE_TAG=$(TAG)

