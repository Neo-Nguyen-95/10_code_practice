

# 1. Create PostgreSQL container

I created a container with this command

```zsh
docker run --name science-question-db \
> -e POSTGRES_PASSWORD=123 \
> -p 127.0.0.1:5433:5432 \
> -v science-question-data:/var/lib/postgresql/data \
> -d postgres:17-bookworm
```

check if the database is ready
```zsh
docker exec science-question-db pg_isready -U postgres
```

Connect to PostgreSQL in terminal
```zsh
docker exec -it science-question-db psql -U postgres -d postgres
```

# 2. Create virtual environment for database practice

At the root directory, run:
```bash
uv venv database/.venv
source database/.venv/bin/activate
uv pip install "psycopg[binary]"
```

# 3. Manipulate database through python
