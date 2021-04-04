FROM ubuntu:16.04

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN apt-get update -y && apt-get install -y python3-pip python3-dev
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt
EXPOSE 5000
COPY . /app
ENV FLASK_APP=app
ENV FLASK_RUN_PORT=5000
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]