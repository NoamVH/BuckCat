FROM python:3.13-slim-bookworm

ADD GCPBackEnd.py .

#ENV TZ=Asia/Jerusalem

#RUN apt-get update && apt-get install -y tzdata

#RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY ./GCPBackEnd.py ./requirements.txt /BuckCat

WORKDIR /BuckCat

RUN pip install --upgrade *

RUN pip install -r ./requirements.txt

CMD [ "python3", "./BackEndQueue.py" ]
