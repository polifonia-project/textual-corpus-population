FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install build-essential libutf8proc-dev -y

WORKDIR ../app

COPY . .

ENV FILE "a.txt"

ENV GROUND_TRUTH "b.txt"

ENV SAVED_FILE "c.txt"

CMD [ "bin/accuracy", "$FILE", "$GROUND_TRUTH", "$SAVED_FILE" ]
