dev:
	python -m app.main

format:
	isort app
	black app
	taplo fmt
