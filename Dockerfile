FROM python:3.11-alpine

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir spotdl
RUN spotdl --download-ffmpeg

RUN dos2unix /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl --fail http://localhost:80/health || exit 1

CMD ["/app/entrypoint.sh"]
