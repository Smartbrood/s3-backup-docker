FROM python:2-alpine
MAINTAINER Andrey N. Petrov <andreynpetrov@gmail.com>

ENV PYTHONUNBUFFERED=1

RUN pip install boto3 schedule

COPY s3-backup.py /usr/local/bin/s3-backup.py

ENTRYPOINT ["/usr/local/bin/s3-backup.py"]


