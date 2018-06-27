FROM python:3.6-slim

WORKDIR /app
RUN useradd user

RUN apt-get update && apt-get install -y make

ADD Makefile .
ADD VERSION .

ADD setup.py .
ADD . .

# build time only:
RUN make install

CMD make test
