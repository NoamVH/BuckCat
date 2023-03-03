FROM python:3.10.10-slim-bullseye

ADD app.py .

ENV TZ=Asia/Jerusalem

RUN apt-get update && apt-get install -y tzdata

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY . /app

WORKDIR /app

RUN pip install --upgrade pip

RUN pip install Flask

CMD [ "python3, "./app.py" ]