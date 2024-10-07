FROM python:3.12

RUN apt update -y
RUN apt install cron -y
RUN echo '*/30 * * * * /usr/src/app/clean.sh' >> /etc/crontab

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY clean.sh .
COPY uploader.py .
COPY static ./static
COPY templates ./templates
COPY flag.txt .

RUN mkdir uploads
RUN chown 1000:1000 uploads
RUN chmod +x clean.sh

EXPOSE 8000

CMD [ "python", "./uploader.py" ]
