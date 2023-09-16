FROM python:3.9-slim

RUN apt update
RUN apt install git -y

COPY . /code
WORKDIR /code
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "main.py" ]