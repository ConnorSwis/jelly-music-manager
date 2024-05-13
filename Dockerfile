FROM python:3.11.5-alpine

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install spotdl
RUN spotdl --download-ffmpeg

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
