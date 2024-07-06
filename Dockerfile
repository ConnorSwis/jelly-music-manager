FROM arm64v8/python:3.11-alpine

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir spotdl
RUN spotdl --download-ffmpeg

RUN dos2unix /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s CMD curl --fail http://localhost:8000/health || exit 1

CMD ["/app/entrypoint.sh"]
