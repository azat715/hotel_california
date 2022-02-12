export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

build:
	docker-compose build

up:
	docker-compose up -d

migrate:
	docker-compose exec backend alembic upgrade head

shell:
	docker-compose exec backend ipython -i -m hotel_california.entrypoints.commands.shell
