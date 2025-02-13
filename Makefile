dev:
	python -m app.main

format:
	isort app
	black app
	isort alembic
	black alembic
	taplo fmt

lint:
	mypy app
	ruff check
