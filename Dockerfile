FROM python:3.9.7-buster

ENV POETRY_VERSION=1.1.0
RUN pip install "poetry==$POETRY_VERSION"

RUN apt-get update && apt-get install -y postgresql-contrib libpq5

WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . /code
CMD ["poetry", "run", "python", "/code/download.py"]
