FROM python:3.11.7

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY pyproject.toml $APP_HOME/pyproject.toml

RUN pip install poetry
RUN pip install jinja2
RUN poetry config virtualenvs.create false && poetry install --only main

COPY . .

EXPOSE 8000

ENTRYPOINT ["python", "main.py"]
