FROM python:3.12

RUN mkdir /mini_crm

WORKDIR /mini_crm

RUN pip install poetry

COPY pyproject.toml poetry.lock* README.md ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root

COPY . .

RUN apt-get update && apt-get install -y dos2unix && \
    dos2unix /mini_crm/docker/*.sh && \
    chmod a+x /mini_crm/docker/*.sh

CMD ["poetry", "run", "gunicorn", "app.main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000"]