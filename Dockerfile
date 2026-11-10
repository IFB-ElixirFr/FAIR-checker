FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    FAIR_CHECKER_HOST=0.0.0.0

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl git gnupg gosu libatomic1 \
    && curl -fsSL https://pgp.mongodb.com/server-8.0.asc \
        | gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg \
    && echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/8.0 main" \
        > /etc/apt/sources.list.d/mongodb-org-8.0.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends mongodb-org-server \
    && mkdir -p /data/db \
    && chown mongodb:mongodb /data/db \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml README.md ./
RUN poetry install --only main --no-interaction --no-ansi
RUN poetry run playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/*

COPY app.py config.py ./
COPY metrics/ metrics/
COPY profiles/ profiles/
COPY templates/ templates/
COPY static/ static/
COPY data/usage_stats.json data/
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

EXPOSE 5000
VOLUME ["/data/db"]

ENTRYPOINT ["sh", "/usr/local/bin/docker-entrypoint.sh"]
CMD ["poetry", "run", "python", "app.py", "--web"]
