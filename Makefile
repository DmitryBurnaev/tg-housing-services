lint:
	poetry run ruff check
	poetry run pyright

format:
	poetry run ruff format
