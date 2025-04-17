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

GCLOUD_PROJECT_ID=careful-granite-450104-s7

GCLOUD_IMAGE_TAG=latest

IMAGE_NAME = us-west2-docker.pkg.dev/$(GCLOUD_PROJECT_ID)/kabuda-backend/api-server

build:
	docker build --platform="linux/amd64" -t $(IMAGE_NAME):$(GCLOUD_IMAGE_TAG) .

push: build
	docker push $(IMAGE_NAME):$(GCLOUD_IMAGE_TAG)

deploy: push
	gcloud builds submit

deploy_only:
	gcloud builds submit

