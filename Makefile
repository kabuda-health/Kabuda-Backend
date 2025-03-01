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
