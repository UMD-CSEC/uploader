FROM python:3.12

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY uploader.py .
COPY static ./static
COPY templates ./templates
COPY flag.txt .

EXPOSE 8000

CMD [ "python", "./uploader.py" ]
