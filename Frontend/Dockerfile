FROM python:3.13-slim-bookworm

ARG PROJECT_ID
ENV PROJECT_ID=${PROJECT_ID}

COPY ./GCPFrontend.py ./requirements.txt /BuckCat/
COPY ./static /BuckCat/static/
COPY ./templates /BuckCat/templates/
WORKDIR /BuckCat

RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

CMD [ "python3", "GCPFrontend.py" ]
