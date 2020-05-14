FROM ubuntu:18.04

RUN apt-get update -y && apt-get install python3.8 -y && apt-get install python3-pip -y

RUN mkdir -p /app

WORKDIR /app

COPY ./requirements.txt .

RUN python3.8 -m pip install -r requirements.txt

COPY . .

EXPOSE 3000

CMD python3.8 app.py

