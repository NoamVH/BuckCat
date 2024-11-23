FROM python:3.13-slim-bookworm

ARG PROJECT_ID
ENV PROJECT_ID=${PROJECT_ID}

COPY ./GCPBackend.py ./requirements.txt /BuckCat/
WORKDIR /BuckCat

RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

CMD [ "python3", "GCPBackend.py" ]
