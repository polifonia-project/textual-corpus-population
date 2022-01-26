FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install tesseract-ocr-all -y \
    python3.8 \
    python3-pip \
    && apt-get install ffmpeg libsm6 libxext6  -y \
    && apt-get install liblcms2-2 libnspr4 libnss3 libpoppler73 poppler-data poppler-utils \
    && apt-get clean \
    && apt-get autoremove

WORKDIR /app

RUN pip3 install --upgrade pip

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "src/ocr_script.py" ]
