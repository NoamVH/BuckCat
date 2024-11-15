FROM python:3.13-slim-bookworm

#ADD GCPBackend.py .

#ENV TZ=Asia/Jerusalem

#RUN apt-get update && apt-get install -y tzdata

#RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY ./GCPBackend.py ./requirements.txt /BuckCat/

WORKDIR /BuckCat

RUN pip install -r ./requirements.txt

CMD [ "python3", "GCPBackend.py" ]
