FROM python:3.9-slim

ENV TZ "Europe/Moscow"
EXPOSE 8000

WORKDIR /home/app
ADD ./app/requirements.txt /home/app
RUN apt-get update && apt-get -y install libpq-dev gcc
RUN pip3 install -r requirements.txt --no-cache-dir
COPY ./app /home/app
RUN chmod +x ./run.sh
CMD ./run.sh
