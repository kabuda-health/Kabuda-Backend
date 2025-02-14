dev:
	uv run -m app.main

format:
	uv run -- ruff check --select I --fix
	uv run -- ruff format
	uv run -- taplo fmt

lint:
	uv run -- mypy app
	uv run -- ruff check

migrate:
	uv run -- alembic upgrade head
