FROM amd64/ubuntu:18.04

RUN apt-get update -y && apt-get install python3.8 -y && apt-get install python3-pip -y

COPY tbb-2020.2-lin.tgz .

RUN tar xzf tbb-2020.2-lin.tgz

RUN cp tbb/lib/intel64/gcc4.8/* /usr/local/lib

RUN mkdir -p /app

WORKDIR /app

COPY ./requirements.txt .

RUN python3.8 -m pip install -r requirements.txt

RUN uname -m

COPY . .

EXPOSE 3000

CMD python3.8 app.py

