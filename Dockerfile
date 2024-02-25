FROM python:3.8-slim-buster

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app

USER 65532:65532

CMD ["python", "api-service.py"]
