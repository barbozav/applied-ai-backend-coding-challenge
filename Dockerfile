FROM python:3.6

RUN mkdir /src
COPY . /src

WORKDIR /src

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

EXPOSE 5000
