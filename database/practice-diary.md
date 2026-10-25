
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