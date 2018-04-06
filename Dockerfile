FROM alpine:3.7
LABEL maintainer "Andrey N. Petrov <andreynpetrov@gmail.com>"

ENV PYTHONUNBUFFERED=1

ENV PACKAGES="\
  dumb-init \
  bash \
  ca-certificates \
  python2 \
  py-setuptools \
  postgresql-client \
"

RUN echo \
  && apk add --no-cache $PACKAGES \
  && if [[ ! -e /usr/bin/python ]];        then ln -sf /usr/bin/python2.7 /usr/bin/python; fi \
  && if [[ ! -e /usr/bin/python-config ]]; then ln -sf /usr/bin/python2.7-config /usr/bin/python-config; fi \
  && if [[ ! -e /usr/bin/easy_install ]];  then ln -sf /usr/bin/easy_install-2.7 /usr/bin/easy_install; fi \
  && easy_install pip \
  && pip install --upgrade pip \
  && if [[ ! -e /usr/bin/pip ]]; then ln -sf /usr/bin/pip2.7 /usr/bin/pip; fi \
  && pip install boto3 schedule \
  && echo

VOLUME ["/backup"]

WORKDIR /backup

COPY s3-backup.py /usr/local/bin/s3-backup.py

#COPY docker-entrypoint.sh /docker-entrypoint.sh

#ENTRYPOINT ["/usr/bin/dumb-init", "bash", "/docker-entrypoint.sh"]

ENTRYPOINT ["/usr/bin/dumb-init", "python", "/usr/local/bin/s3-backup.py"]
