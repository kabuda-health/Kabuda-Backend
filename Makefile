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

TAG ?= $(shell echo $$GCLOUD_IMAGE_TAG)

PROJECT_ID := $(shell echo $$GCLOUD_PROJECT_ID)

IMAGE_NAME = us-west2-docker.pkg.dev/$(PROJECT_ID)/kabuda-backend/api-server

build:
	docker build --platform="linux/amd64" -t $(IMAGE_NAME):$(TAG) .

push: build
	docker push $(IMAGE_NAME):$(TAG)

deploy: push
	envsubst < k8s.yaml > deploy.yaml
	gcloud builds submit

deploy_only:
	envsubst < k8s.yaml > deploy.yaml
	gcloud builds submit

