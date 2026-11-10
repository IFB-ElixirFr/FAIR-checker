FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    FAIR_CHECKER_HOST=0.0.0.0

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git libatomic1 \
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

EXPOSE 5000

CMD ["poetry", "run", "python", "app.py", "--web"]
