# syntax=docker/dockerfile:1
FROM python:3.10-slim

# Identify the maintainer of an image
LABEL maintainer="mike.bison42@googlemail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# docker best practices:
# put all changes to the image at the end of the file to create less layers

# Update the image to the latest packages
# use && to reduce the amount of layers created
RUN apt-get update -y  \
    && apt-get install -y git  \
    && rm -rf /var/lib/apt/lists/{apt,dpkg,cache,log} /tmp/* /var/tmp/*  # clean up

# pip install
COPY ./requirements.txt /requirements.txt
RUN pip install -U pip
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

COPY . /app

# create an empty .env-file to be safely set as a parameter and overmount externally
RUN touch .env

CMD ["sh", "-c", "uvicorn main:app --host \"${HOST:-0.0.0.0}\" --port \"${PORT:-8080}\" --workers \"${WORKERS:-4}\" --env-file .env"]

# old CMD for refference
# yes, i probably should just delete this because git... well i just had done this i guess ^^"
# fastapi run main.py --port 8080 --proxy-headers
#CMD ["fastapi", "run", "main.py", "--port", "8080", "--proxy-headers"]
#CMD ["uvicorn", "main:app", "--host", "${HOST:-0.0.0.0}", "--port", "${PORT:-8080}", "--workers", "4", "--env-file", ".env"]
