FROM python:3.11.7

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY . .

RUN pip install poetry

EXPOSE 8000

ENTRYPOINT ["python", "main.py"]
