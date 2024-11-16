FROM python:3.10.10-slim-bullseye

ADD appQueue.py .

#ENV TZ=Asia/Jerusalem

#RUN apt-get update && apt-get install -y tzdata

#RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY . /app

WORKDIR /app

RUN pip install --upgrade pip

RUN pip install boto3

RUN pip install Flask

CMD [ "python3", "./appQueue.py" ]