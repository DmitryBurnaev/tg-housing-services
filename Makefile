lint:
	poetry run ruff check
	poetry run pyright

format:
	poetry run ruff format

run:
	PYTHONPATH=. poetry run python src/main.py

test:
	PYTHONPATH=. poetry run pytest src/tests

docker-run:
	docker compose up --build bot

docker-test:
	docker compose up --build test
